import uvicorn
from argparse import ArgumentParser
from web.settings import PROD_UVICORN_CONFIG, DEV_UVICORN_CONFIG


parser = ArgumentParser('Transpiler Web')
parser.add_argument('-D', '--dev', action='store_true')

args = parser.parse_args()

uvicorn_config = DEV_UVICORN_CONFIG if args.dev else PROD_UVICORN_CONFIG

uvicorn.run(**uvicorn_config)
