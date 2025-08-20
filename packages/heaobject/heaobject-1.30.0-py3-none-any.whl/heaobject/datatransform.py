from .root import AbstractDesktopObject, make_abstract
from abc import ABC


class DataTransform(AbstractDesktopObject, ABC):
    def __new__(cls, *args, **kwargs):
        return make_abstract(DataTransform, cls, *args, **kwargs)
