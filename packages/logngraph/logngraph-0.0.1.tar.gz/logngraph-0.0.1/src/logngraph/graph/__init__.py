from logngraph.errors import *

try:
    import pygame
except ImportError:
    raise FeatureNotInstalledError("graph feature not installed! Install using `pip install logngraph[graph]` first!")

from logngraph.graph.graph import *
