# principal_package/__init__.py

from .funtions import (
    np, pd, sns, plt, px, pio,
    clearing_description,
    cluster_model, silhouette,
    NLP_Reductor, Principal_components, map_separate_clusters, date_processing,
    map_conserve_structure,
    GeneradorPlantillas,
    tqdm, multiprocess, delayed
)

__version__ = "0.1.2"

# OPCIONAL: define __all__ para claridad y para from principal_package import *
__all__ = [
    "np", "pd", "sns", "plt", "px", "pio",
    "clearing_description",
    "cluster_model", "silhouette",
    "NLP_Reductor", "Principal_components", "map_separate_clusters", "date_processing",
    "map_conserve_structure",
    "GeneradorPlantillas",
    "tqdm", "multiprocess", "delayed",
    "__version__",
]
