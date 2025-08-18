from typing import List
from datetime import datetime, time
from pydantic import BaseModel

from .types import *


class LisOut(BaseModel):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()
