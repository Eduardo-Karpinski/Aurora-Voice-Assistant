import re

import primp
from ddgs import DDGS
from ddgs.exceptions import DDGSException, TimeoutException
from ddgs.http_client import HttpClient

MAX_RESULTS = 5
SNIPPET_LIMIT = 240
PAGE_LIMIT = 800

def pesquisar(consulta):
    consulta = (consulta or "").strip()
    if not consulta:
        return "A pesquisa veio sem texto."

    _navegador()
    try:
        ddgs = DDGS(timeout=12)
        results = ddgs.text(consulta, region="br-pt", max_results=MAX_RESULTS) or []
    except TimeoutException:
        return "A pesquisa na internet falhou."
    except DDGSException:
        results = []
    if not results:
        return "A pesquisa não encontrou resultado."

    lines = []
    page = _pagina(ddgs, results)
    if page:
        lines.append(page)
    for item in results:
        title = str(item.get("title") or "").strip()
        body = " ".join(str(item.get("body") or "").split())
        if len(body) > SNIPPET_LIMIT:
            body = body[:SNIPPET_LIMIT].rstrip() + "..."
        if title or body:
            lines.append(f"{title}. {body}".strip())
    return "\n".join(lines) if lines else "A pesquisa não encontrou resultado."

def _navegador():
    # O cliente da biblioteca sorteia um navegador a cada pedido. O perfil de
    # celular devolve um HTML que os motores não conseguem ler.
    def __init__(self, proxy=None, timeout=10, *, verify=True):
        self.client = primp.Client(
            proxy=proxy,
            timeout=timeout,
            impersonate="chrome_146",
            impersonate_os="windows",
            verify=verify if isinstance(verify, bool) else True,
        )

    HttpClient.__init__ = __init__

def _pagina(ddgs, results):
    for item in results[:2]:
        href = item.get("href")
        if not href:
            continue
        try:
            page = ddgs.extract(href, fmt="text_markdown")
        except Exception:
            continue
        text = str(page.get("content") or "")
        heading = re.search(r"(?m)^#+ ", text)
        if heading:
            text = text[heading.start():]
        text = " ".join(text.split())
        if len(text) < 80:
            continue
        if len(text) > PAGE_LIMIT:
            text = text[:PAGE_LIMIT].rstrip() + "..."
        return text
    return ""
