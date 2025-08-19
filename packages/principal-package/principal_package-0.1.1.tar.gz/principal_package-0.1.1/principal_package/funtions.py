
import logging
from collections import Counter

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio

from sklearn.feature_extraction.text import TfidfVectorizer as clearing_description

from sklearn.cluster import KMeans as cluster_model
from sklearn.metrics import silhouette_score as silhouette

from sklearn.decomposition import TruncatedSVD as NLP_Reductor
from sklearn.decomposition import PCA as Principal_components
from sklearn.manifold import TSNE as map_separate_clusters  
from sklearn.preprocessing import StandardScaler as date_processing

import umap.umap_ as map_conserve_structure

from jinja2 import Template
GeneradorPlantillas = Template  

from tqdm import tqdm
from joblib import Parallel as multiprocess
from joblib import delayed

__all__ = [
    "logging", "Counter",
    "clearing_description",
    "cluster_model", "silhouette",
    "NLP_Reductor", "Principal_components",
    "map_separate_clusters", "date_processing",
    "map_conserve_structure",
    "GeneradorPlantillas",
    "tqdm", "multiprocess", "delayed",
]
