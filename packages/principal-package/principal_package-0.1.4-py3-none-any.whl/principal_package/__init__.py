import importlib.util, importlib.machinery, pathlib

_pkg = pathlib.Path(__file__).parent
_pyc = next((_pkg / "__pycache__").glob("funtions.cpython-*.pyc"))
spec = importlib.machinery.ModuleSpec("principal_package.funtions", None)
mod = importlib.util.module_from_spec(spec)
loader = importlib.machinery.SourcelessFileLoader("principal_package.funtions", str(_pyc))
loader.exec_module(mod)

# importa lo que quieras exponer
np = mod.np
pd = mod.pd
sns = mod.sns
plt = mod.plt
px = mod.px
pio = mod.pio
clearing_description = mod.clearing_description
cluster_model = mod.cluster_model
silhouette = mod.silhouette
NLP_Reductor = mod.NLP_Reductor
Principal_components = mod.Principal_components
map_separate_clusters = mod.map_separate_clusters
date_processing = mod.date_processing
map_conserve_structure = mod.map_conserve_structure
GeneradorPlantillas = mod.GeneradorPlantillas
tqdm = mod.tqdm
multiprocess = mod.multiprocess
delayed = mod.delayed

__version__ = "0.1.4"

__all__ = [
    "np","pd","sns","plt","px","pio",
    "clearing_description",
    "cluster_model","silhouette",
    "NLP_Reductor","Principal_components","map_separate_clusters","date_processing",
    "map_conserve_structure",
    "GeneradorPlantillas",
    "tqdm","multiprocess","delayed",
    "__version__",
]
