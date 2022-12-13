import traceback
from fastapi.responses import HTMLResponse
from transpiler.base import TranspilerError
from transpiler import transpile
from web import app
from web.settings import STATIC_DIR
from web.schemas import Code, TranspileResult


@app.get('/')
async def get_page() -> HTMLResponse:
    return HTMLResponse((STATIC_DIR / 'index.html').read_bytes())


@app.post('/transpile')
async def get_transpiled(code: Code) -> TranspileResult:
    try:
        result = transpile(code.code)
        return TranspileResult(
            result=result,
            success=True,
        )
    except TranspilerError as error:
        traceback.print_exc()
        return TranspileResult(
            result=f'{error.__class__.__name__}: {error}',
            success=False,
        )
