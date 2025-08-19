import logging
from collections import Counter
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio

import importlib.util, importlib.machinery, pathlib, glob

_pkg = pathlib.Path(__file__).parent
_pycache = _pkg / "__pycache__"

# Busca funtions.cpython-*.pyc
matches = glob.glob(str(_pycache / "funtions.cpython-*.pyc"))
if not matches:
    raise ImportError(
        "No se encontró '__pycache__/funtions.cpython-*.pyc'. "
        "Compila antes con: python -m compileall principal_package"
    )

_pyc_path = matches[0]
loader = importlib.machinery.SourcelessFileLoader("principal_package.funtions", _pyc_path)
spec = importlib.machinery.ModuleSpec("principal_package.funtions", loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)
clearing_description   = mod.clearing_description
cluster_model          = mod.cluster_model
silhouette             = mod.silhouette
NLP_Reductor           = mod.NLP_Reductor
Principal_components   = mod.Principal_components
map_separate_clusters  = mod.map_separate_clusters
date_processing        = mod.date_processing
map_conserve_structure = mod.map_conserve_structure
GeneradorPlantillas    = mod.GeneradorPlantillas
tqdm                   = mod.tqdm
multiprocess           = mod.multiprocess
delayed                = mod.delayed

__version__ = "0.1.7"

__all__ = [
    "logging", "Counter",
    "np", "pd", "sns", "plt", "px", "pio",
    "clearing_description",
    "cluster_model", "silhouette",
    "NLP_Reductor", "Principal_components",
    "map_separate_clusters", "date_processing",
    "map_conserve_structure",
    "GeneradorPlantillas",
    "tqdm", "multiprocess", "delayed",
    "__version__",
]
