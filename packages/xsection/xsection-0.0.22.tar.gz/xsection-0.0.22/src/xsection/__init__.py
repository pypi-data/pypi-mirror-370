from dataclasses import dataclass, fields
from collections.abc import Mapping

from ._types import SectionType
from .polygon import PolygonSection
from .composite import CompositeSection
from . import library



class Material:
    E : float = 0
    G : float = 0
    Fy: float = 0
    name: str = ""
    type: str = ""



class Section(SectionType):
    _is_fiber:     bool
    _is_shape:     bool
    _is_model:     bool

    # For parsing
    def __init__(self,
                 elastic=None,
                 plastic=None,
                 composite=False,
                 fiber=None,
                 model=None,
                 mesh = None,
                 shape=None):
        pass

    def translate(self, location):
        """
        Translate the section to a new location.
        """

    def rotate(self,    angle: float): ...

    @property 
    def elastic(self)-> "ElasticConstants":
        """
        An object holding the elastic properties of a section.
        """

    def create_fibers(self, mesh_scale=None, **kwds): ...
        

    def linspace(self, start, stop, num, radius=None, **kwds):
        """
        Create ``num`` copies of this section with centroids linearly aranged from ``start`` to ``stop``.
        """



class FiberSection(Section):
    def __init__(self, fibers, **kwds):
        pass

    @classmethod
    def from_fibers(cls, fibers, **kwds):
        pass 


def from_structure(model, tag):
    pass



@dataclass
class PlasticConstants(Mapping):
    Zy: float
    Zz: float
    Sy: float
    Sz: float

    def __getitem__(self, key):
        # Allows accessing attributes by key.
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __iter__(self):
        # Iterate over field names.
        return (f.name for f in fields(self))

    def __len__(self):
        # Number of fields.
        return len(fields(self))


@dataclass
class ElasticConstants(Mapping):
    Iy: float
    Iz: float
    A:  float
    Ay: float = None
    Az: float = None
    J:  float = None
    E:  float = 0
    G:  float = 0

    Iyz: float = 0

    def __getitem__(self, key):
        # Allows accessing attributes by key.
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __iter__(self):
        # Iterate over field names.
        return (f.name for f in fields(self))

    def __len__(self):
        # Number of fields.
        return len(fields(self))


def read(filename):
    import xcae 
    tree = xcae.load(filename)
    