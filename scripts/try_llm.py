import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import llm

# python scripts/try_llm.py What is the temperature on the surface of the Moon?
question = " ".join(sys.argv[1:]).strip() or "What is the temperature on the surface of the Moon?"
llm.init()
print(llm.ask(question))
