from pathlib import Path


WEB_ROOT = Path(__file__).parent.resolve().absolute()


BASE_UVICORN_CONFIG = {
    'app': 'web.app:app',
    'host': '0.0.0.0',
    'port': 8000,
}

PROD_UVICORN_CONFIG = BASE_UVICORN_CONFIG
DEV_UVICORN_CONFIG = {
    **BASE_UVICORN_CONFIG,
    'reload': True,
}

STATIC_DIR = WEB_ROOT / 'static'
