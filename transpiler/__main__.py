import sys
from pathlib import Path
from transpiler.settings import EXAMPLES_DIR
from transpiler import transpile


filepath = sys.argv[1]

code = Path(filepath).read_text()
sharp_code = transpile(code)

new_filename = f'{filepath.rsplit("/", maxsplit=1)[-1]}.cs'
(EXAMPLES_DIR / new_filename).write_text(sharp_code, encoding='utf-8')
