from typing import Union
from .adr import Adr
from .auftrag import Auftrag
from .ende import Ende
from .ggut import Ggut
from .ladeli import Ladeli
from .lademi import Lademi
from .posit import Posit
from .start import Start
from .text import Text
from .geb import Geb
from .dmsdok import DmsDok
from .dmsref import DmsRef
from .dmssw import DmsSw
from .status import Status


RecordTypes = Union[
    Auftrag,
    Ende,
    Ggut,
    Ladeli,
    Lademi,
    Posit,
    Start,
    Text,
    Adr,
    Geb,
    DmsDok,
    DmsRef,
    DmsSw,
    Status,
]
