import os
import re
import logging


logging.basicConfig(
    format='%(levelname)s:[%(module)s:%(lineno)d]: %(message)s',
    level=os.getenv('LOG_LEVEL', logging.WARNING),
)


LEXER_REGEX_FLAGS = re.IGNORECASE
