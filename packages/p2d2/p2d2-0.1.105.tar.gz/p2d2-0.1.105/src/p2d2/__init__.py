from pathlib import Path
from types import MethodType

import pandas as pd
from jinja2 import Environment, FileSystemLoader
from loguru import logger as log
from pandas import DataFrame

DEBUG = True
CWD = Path(__file__).parent
TEMPLATES = CWD / "templates"
CWD_TEMPLATER = Environment(loader=FileSystemLoader(TEMPLATES))
STATIC = CWD / "static"

from .database import Database

title_col = "col1"
subtitle_col = "col2"
d = {title_col: [1, 2], subtitle_col: [3, 4]}
df = pd.DataFrame(data=d)