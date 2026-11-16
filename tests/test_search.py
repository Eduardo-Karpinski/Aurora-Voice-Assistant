from aurora.config import SearchConfig
from aurora.language.search import search


class FakeSearch:
    def __init__(self, results=None, pages=None, error=None):
        self.results = results or []
        self.pages = pages or {}
        self.error = error
        self.queries = []

    def text(self, query, region, max_results):
        self.queries.append((query, region, max_results))
        if self.error:
            raise self.error
        return self.results

    def extract(self, href, fmt):
        if href not in self.pages:
            raise RuntimeError(href)
        return {"content": self.pages[href]}


class TimeoutException(Exception):
    pass


class DDGSException(Exception):
    pass


def test_search_rejects_an_empty_query_without_calling_the_client():
    client = FakeSearch()
    assert search("   ", client=client) == "The search query was empty."
    assert client.queries == []


def test_search_reports_a_timeout():
    client = FakeSearch(error=TimeoutException("slow"))
    assert search("dollar", client=client) == "The web search failed."


def test_search_reports_an_empty_engine_response():
    client = FakeSearch(error=DDGSException("blocked"))
    assert search("dollar", client=client) == "The search returned no results."


def test_search_formats_the_page_and_truncates_snippets():
    body = "x" * (SearchConfig.SNIPPET_LIMIT + 20)
    page = "# Rate\n\n" + ("The dollar is at five reais today. " * 6)
    client = FakeSearch(
        results=[
            {"title": "Dollar", "body": body, "href": "https://example.com/rate"},
            {"title": "", "body": "short page", "href": "https://example.com/skip"},
        ],
        pages={
            "https://example.com/rate": page,
            "https://example.com/skip": "too short",
        },
    )
    text = search("cotação", client=client)
    assert client.queries == [("cotação", SearchConfig.REGION, SearchConfig.MAX_RESULTS)]
    page_line, snippets = text.split("\n", 1)
    assert page_line.startswith("# Rate The dollar is at five reais today.")
    assert len(page_line) <= SearchConfig.PAGE_LIMIT + len("...")
    assert snippets.startswith("Dollar. ")
    assert snippets.endswith("short page")
    assert "..." in snippets
