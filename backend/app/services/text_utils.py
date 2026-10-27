"""Text helpers for article payloads.

Feed adapters put the *whole article* into the feed's ``summary`` field as raw
HTML and leave ``content`` empty (see ``app/adapters/rss_base.py`` and
``rsshub_base.py``). The UI treats ``summary`` as plain text — the list renders
it with a text interpolation and the reader falls back to it when ``content``
is missing — so the markup used to reach the screen verbatim: every list row
showed ``<p>…`` and the reader escaped the whole body into visible tags.

``split_article_text`` puts the two fields back on their intended contract:
``summary`` is readable plain text, ``content`` is the HTML body.
"""

import html as html_lib
import re

# <script>/<style> bodies would otherwise leak their code into the preview.
_SCRIPT_RE = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
# Block-level closing tags become line breaks so the text keeps its shape.
_BLOCK_RE = re.compile(r"<\s*(?:br|/p|/div|/li|/tr|/h[1-6]|/blockquote)\s*/?>", re.I)
_TAG_RE = re.compile(r"<[^>]+>")
# Only *known* tag names count as markup. A generic "<...>" match would treat
# plain text such as "价格从 <10元 涨到 >20元" as HTML and delete that span
# when it is stripped.
_HTML_TAG_RE = re.compile(
    r"</?(?:p|br|hr|div|span|a|img|ul|ol|li|dl|dt|dd|h[1-6]|blockquote|"
    r"strong|b|em|i|u|s|sup|sub|small|table|thead|tbody|tfoot|tr|td|th|"
    r"pre|code|figure|figcaption|section|article|header|footer|main|nav|aside)"
    r"\b[^>]*>",
    re.I,
)
_SPACE_RE = re.compile(r"[ \t\r\f\v]+")
_BLANK_LINES_RE = re.compile(r"\n{3,}")


def looks_like_html(value: str | None) -> bool:
    """True when the string contains real HTML markup.

    Only known tag names count. Matching any "<...>" would classify ordinary
    text that happens to contain angle brackets as markup, and the text would
    then be silently mangled.
    """
    return bool(value) and bool(_HTML_TAG_RE.search(value))


def strip_html(value: str | None) -> str:
    """Turn an HTML fragment into readable plain text."""
    if not value:
        return ""
    text = _SCRIPT_RE.sub(" ", value)
    text = _BLOCK_RE.sub("\n", text)
    text = _TAG_RE.sub("", text)
    text = html_lib.unescape(text)
    text = _SPACE_RE.sub(" ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = _BLANK_LINES_RE.sub("\n\n", text)
    return text.strip()


def to_plain_text(value: str | None) -> str:
    """Plain text from a value that may still carry HTML.

    Used for values read straight from the database, where rows stored before
    the write-path fix still hold the feed's HTML in ``summary``. Values that
    are already plain text are returned verbatim, so a summary that merely
    contains angle brackets is not damaged.
    """
    if not value:
        return ""
    if looks_like_html(value):
        return strip_html(value)
    return value


def split_article_text(
    summary: str | None, content: str | None
) -> tuple[str, str | None]:
    """Return ``(plain_text_summary, html_body)`` for a stored/served article.

    * A summary that is really HTML becomes the body (``content``) when the
      feed did not provide one, and its readable text becomes the summary.
    * A summary that is already plain text is kept as the summary, and the
      body is left alone.
    """
    summary = summary or ""
    content = content or None

    if content is None and looks_like_html(summary):
        content = summary

    text = to_plain_text(summary)
    if not text and content:
        text = strip_html(content)[:200]
    return text, content
