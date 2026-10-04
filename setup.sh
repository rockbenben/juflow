#!/bin/sh
# One-shot deploy bootstrap: creates .env from the template and fills the
# two secrets with random values. Idempotent — never overwrites a value you
# already changed by hand; only replaces empty or template-placeholder ones.
# Windows PowerShell / cmd without a POSIX shell: use the manual "Path B"
# documented in the README quick start instead of this script.
set -eu
cd "$(dirname "$0")"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "已生成 .env / Created .env from template"
fi

gen() { openssl rand -hex 32; }

patch() {
  # $1 key, $2 new value — replaces only empty or known placeholder values
  cur=$(grep "^$1=" .env | head -1 | cut -d= -f2- || true)
  case "$cur" in
    ""|change-me-in-production|juflow_dev)
      if grep -q "^$1=" .env; then
        sed "s|^$1=.*|$1=$2|" .env > .env.tmp && mv .env.tmp .env
      else
        echo "$1=$2" >> .env
      fi
      echo "- $1 已随机填充 / $1 set to a random value"
      ;;
    *)
      echo "- $1 保持你已设置的值 / $1 left as configured"
      ;;
  esac
}

patch SECRET_KEY "$(gen)"
patch POSTGRES_PASSWORD "$(gen | cut -c1-24)"

# The backend connects via DATABASE_URL, which embeds the password — keep them in sync.
PW=$(grep '^POSTGRES_PASSWORD=' .env | cut -d= -f2-)
if grep -q ':juflow_dev@' .env; then
  sed "s|:juflow_dev@|:${PW}@|" .env > .env.tmp && mv .env.tmp .env
  echo "- DATABASE_URL 已同步新密码 / DATABASE_URL password synced"
fi

echo
echo "下一步 / Next:  docker compose up -d   →   http://localhost"
echo "注意：数据库口令只在卷的首次初始化时生效；若之前已 up 过（pgdata 已存在），"
echo "改密码后需同步库内口令（ALTER ROLE）或清空 pgdata 卷重建。"
