import traceback
from fastapi.responses import HTMLResponse
from transpiler.base import TranspilerError
from web import app
from web.settings import STATIC_DIR
from web.schemas import Code, TranspileResult
from web.backend import transpile


@app.get('/')
async def get_page() -> HTMLResponse:
    return HTMLResponse((STATIC_DIR / 'index.html').read_bytes())


@app.post('/transpile')
async def get_transpiled(code: Code) -> TranspileResult:
    try:
        return TranspileResult(result=transpile(code.code), success=True).json()
    except TranspilerError:
        traceback.print_exc()
        return TranspileResult(
            result=traceback.format_exc(),
            success=False,
        )
