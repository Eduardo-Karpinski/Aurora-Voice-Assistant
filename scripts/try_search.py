import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from search import search

# python scripts/try_search.py current dollar to real exchange rate
query = " ".join(sys.argv[1:]).strip() or "current dollar to real exchange rate"
print(search(query))
