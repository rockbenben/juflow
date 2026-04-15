import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.plugin_loader import plugin_loader
from app.models.installed_plugin import InstalledPlugin


PLUGINS_DIR = Path("plugins/adapters")


async def list_plugins(db: AsyncSession) -> list[InstalledPlugin]:
    result = await db.execute(select(InstalledPlugin).order_by(InstalledPlugin.installed_at.desc()))
    return list(result.scalars().all())


async def install_from_git(db: AsyncSession, url: str) -> InstalledPlugin:
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        subprocess.run(
            ["git", "clone", "--depth", "1", url, tmp_dir],
            check=True, capture_output=True, text=True,
        )
        return await _install_from_dir(db, Path(tmp_dir))


async def install_from_zip(db: AsyncSession, zip_data: bytes) -> InstalledPlugin:
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = Path(tmp_dir) / "plugin.zip"
        zip_path.write_bytes(zip_data)
        extract_dir = Path(tmp_dir) / "extracted"
        with zipfile.ZipFile(zip_path) as zf:
            # Prevent zip-slip path traversal
            for info in zf.infolist():
                target = (extract_dir / info.filename).resolve()
                if not str(target).startswith(str(extract_dir.resolve())):
                    raise ValueError(f"Zip contains path traversal: {info.filename}")
            zf.extractall(extract_dir)
        # Find the directory that contains manifest.json
        manifest_candidates = list(extract_dir.rglob("manifest.json"))
        if not manifest_candidates:
            raise ValueError("No manifest.json found in zip archive")
        plugin_source_dir = manifest_candidates[0].parent
        return await _install_from_dir(db, plugin_source_dir)


async def _install_from_dir(db: AsyncSession, source_dir: Path) -> InstalledPlugin:
    import json
    import re
    manifest_path = source_dir / "manifest.json"
    if not manifest_path.exists():
        raise ValueError(f"manifest.json not found in {source_dir}")
    with open(manifest_path) as f:
        manifest = json.load(f)
    name = manifest["name"]
    # Prevent path traversal via plugin name
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        raise ValueError(f"Invalid plugin name: {name}. Only alphanumeric, hyphens, and underscores allowed.")
    dest_dir = PLUGINS_DIR / name
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    shutil.copytree(source_dir, dest_dir)

    # Remove existing DB record if any
    existing = await db.execute(select(InstalledPlugin).where(InstalledPlugin.name == name))
    existing_plugin = existing.scalar_one_or_none()
    if existing_plugin:
        await db.delete(existing_plugin)
        await db.flush()

    plugin = InstalledPlugin(
        name=name,
        display_name=manifest.get("display_name", name),
        version=manifest.get("version", "0.0.0"),
        author=manifest.get("author", ""),
        description=manifest.get("description", ""),
        adapter_class=manifest["adapter_class"],
        enabled=True,
    )
    db.add(plugin)
    await db.commit()
    await db.refresh(plugin)

    # Load into registry
    plugin_loader.load_plugin(str(dest_dir))
    return plugin


async def uninstall_plugin(db: AsyncSession, name: str) -> bool:
    result = await db.execute(select(InstalledPlugin).where(InstalledPlugin.name == name))
    plugin = result.scalar_one_or_none()
    if not plugin:
        return False
    # Unload from registry
    plugin_loader.unload_plugin(name)
    # Delete directory
    dest_dir = PLUGINS_DIR / name
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    # Delete DB record
    await db.delete(plugin)
    await db.commit()
    return True


async def toggle_plugin(db: AsyncSession, name: str, enable: bool) -> InstalledPlugin | None:
    result = await db.execute(select(InstalledPlugin).where(InstalledPlugin.name == name))
    plugin = result.scalar_one_or_none()
    if not plugin:
        return None
    plugin.enabled = enable
    await db.commit()
    await db.refresh(plugin)
    dest_dir = PLUGINS_DIR / name
    if enable:
        plugin_loader.load_plugin(str(dest_dir))
    else:
        plugin_loader.unload_plugin(name)
    return plugin
