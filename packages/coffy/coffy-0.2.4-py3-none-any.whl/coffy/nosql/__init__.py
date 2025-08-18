# coffy/nosql/__init__.py
# author: nsarathy

from .engine import CollectionManager


def db(collection_name: str, path: str = None):
    return CollectionManager(collection_name, path=path)


__all__ = ["db", "CollectionManager"]
