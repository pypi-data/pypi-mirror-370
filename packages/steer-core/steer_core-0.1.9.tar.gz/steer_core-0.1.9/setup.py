from setuptools import setup, find_packages
import pathlib
import re

root = pathlib.Path(__file__).parent
init = root / "steer_core" / "__init__.py"
version = re.search(r'__version__\s*=\s*"([^"]+)"', init.read_text()).group(1)

setup(
    name='steer-core',
    version=version, 
    description='Modelling energy storage from cell to site - STEER OpenCell Design',
    author='Nicholas Siemons',
    author_email='nsiemons@stanford.edu',
    url="https://github.com/nicholas9182/steer-core/",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas==2.1.4",
        "numpy==1.26.4",
        "datetime==5.5",
        "scipy==1.15.3",
        "plotly==6.2.0",
    ],
    package_data={"steer_core.Data": ["database.db"]},
    scripts=[],
    classifiers=[ 
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
