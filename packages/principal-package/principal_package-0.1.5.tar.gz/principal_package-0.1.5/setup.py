
from pathlib import Path
from setuptools import setup, find_packages

this_dir = Path(__file__).parent
readme_path = this_dir / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="principal_package",             
    version="0.1.5",
    description="Librería en Python para clustering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sebastian Castro",        
    license="MIT",                    
    packages=find_packages(exclude=("tests", "docs", "examples")),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21",
        "pandas>=1.3",
        "matplotlib>=3.5",
        "seaborn>=0.11",
        "plotly>=5.0",
        "scikit-learn>=1.0",
        "umap-learn>=0.5",
        "tqdm>=4.64",
        "joblib>=1.1",
        "jinja2>=3.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Intended Audience :: Science/Research",
    ],
)
