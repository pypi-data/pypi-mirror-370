"""
Storage pluggable para PyWhatsWeb
"""

from .base import BaseStore
from .filesystem import FileSystemStore
from .django import DjangoORMStore

__all__ = [
    "BaseStore",
    "FileSystemStore", 
    "DjangoORMStore",
]
