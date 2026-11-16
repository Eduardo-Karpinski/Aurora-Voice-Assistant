import re

from aurora.config import SearchConfig

# ddgs 9.16.1 picks a random browser profile on every request. A mobile profile
# returns HTML the engines cannot read, so the constructor below forces desktop
# Chrome on Windows. HttpClient.__init__ is private; keep the ddgs pin in
# requirements.txt in step with this patch.
_DESKTOP_CHROME_READY = False


def search(query, client=None):
    query = (query or "").strip()
    if not query:
        return "The search query was empty."

    if client is None:
        client = _client()

    results = _results(client, query)
    if results is None:
        return "The web search failed."
    if not results:
        return "The search returned no results."

    return _format(results, _page(client, results))


def _client():
    _use_desktop_chrome()
    from ddgs import DDGS

    return DDGS(timeout=SearchConfig.TIMEOUT)


def _use_desktop_chrome():
    global _DESKTOP_CHROME_READY
    if _DESKTOP_CHROME_READY:
        return

    import primp
    from ddgs.http_client import HttpClient

    def __init__(self, proxy=None, timeout=10, *, verify=True):
        self.client = primp.Client(
            proxy=proxy,
            timeout=timeout,
            impersonate="chrome_146",
            impersonate_os="windows",
            verify=verify if isinstance(verify, bool) else True,
        )

    HttpClient.__init__ = __init__
    _DESKTOP_CHROME_READY = True


def _results(client, query):
    try:
        return client.text(
            query,
            region=SearchConfig.REGION,
            max_results=SearchConfig.MAX_RESULTS,
        ) or []
    except Exception as exc:
        if type(exc).__name__ == "TimeoutException":
            return None
        if type(exc).__name__ == "DDGSException":
            return []
        raise


def _page(client, results):
    for item in results[:2]:
        href = item.get("href")
        if not href:
            continue
        try:
            page = client.extract(href, fmt="text_markdown")
        except Exception:
            continue
        text = _page_text(str(page.get("content") or ""))
        if text:
            return text
    return ""


def _page_text(text):
    heading = re.search(r"(?m)^#+ ", text)
    if heading:
        text = text[heading.start():]
    text = " ".join(text.split())
    if len(text) < 80:
        return ""
    limit = SearchConfig.PAGE_LIMIT
    if len(text) > limit:
        text = text[:limit].rstrip() + "..."
    return text


def _snippet(title, body):
    title = str(title or "").strip()
    body = " ".join(str(body or "").split())
    limit = SearchConfig.SNIPPET_LIMIT
    if len(body) > limit:
        body = body[:limit].rstrip() + "..."
    parts = [part for part in (title, body) if part]
    return ". ".join(parts)


def _format(results, page):
    lines = []
    if page:
        lines.append(page)
    for item in results:
        line = _snippet(item.get("title"), item.get("body"))
        if line:
            lines.append(line)
    if not lines:
        return "The search returned no results."
    return "\n".join(lines)
