import importlib.metadata

# # Importation du module C++ généré par pybind11
# from .jerboapy_bin import *

# # Lecture automatique des métadonnées depuis pyproject.toml
# __version__ = importlib.metadata.version("jerboapy")
# __description__ = importlib.metadata.metadata("jerboapy")["Summary"]
# __author__ = importlib.metadata.metadata("jerboapy")["Authors"]
# __license__ = importlib.metadata.metadata("jerboapy")["License"]

# Importation du module C++ généré par pybind11
from .jerboapy_bin import *

# Gestion sécurisée des métadonnées
try:
    import importlib.metadata
    __version__ = importlib.metadata.version("jerboapy")
    __description__ = importlib.metadata.metadata("jerboapy")["Summary"]
    __author__ = importlib.metadata.metadata("jerboapy")["Author-Email"]
    if not __author__:
        __author__ = importlib.metadata.metadata("jerboapy")["Author"]
    __license__ = importlib.metadata.metadata("jerboapy")["License-Expression"]
    if not __license__:
        __license__ = importlib.metadata.metadata("jerboapy")["License"]
except (ImportError, importlib.metadata.PackageNotFoundError):
    # Valeurs par défaut si le package n'est pas installé
    __version__ = "X.X.X-dev"
    __description__ = "Jerboa C++ bindings for Python (dev version without metadata)"
    __author__ = "Hakim"
    __license__ = "GPL-3.0-or-later"