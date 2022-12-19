from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from web.settings import STATIC_DIR


app = FastAPI()

app.mount(
    '/static',
    StaticFiles(directory=STATIC_DIR),
    name='static'
)
