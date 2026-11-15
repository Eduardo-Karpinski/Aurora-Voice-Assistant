import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import llm

# python tests/test_llm.py qual a cotacao do dolar para real agora?
pergunta = " ".join(sys.argv[1:]).strip() or "Qual a temperatura da superficie da lua?"
llm.init()
print(llm.ask(pergunta))
