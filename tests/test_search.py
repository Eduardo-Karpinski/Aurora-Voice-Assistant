import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from search import pesquisar

# python tests/test_search.py cotacao do dolar para real agora
consulta = " ".join(sys.argv[1:]).strip() or "cotacao do dolar para real agora"
print(pesquisar(consulta))
