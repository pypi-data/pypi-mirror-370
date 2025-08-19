from setuptools import setup, find_packages

requirements = [
    'deepdiff',
    'streamlit',
    'opensearch-py',
    'spacy',
    'spacy-udpipe',
    'pymupdf4llm',
    'pypandoc',
    'tqdm',
    'sentence-transformers',
    'wandb',
    'optuna',
    'datasets',
    'openpyxl',
    'pandas',
    'matplotlib',
    'transformers',
    'transformers[torch]',
    'wikipedia',
    'twine'
]

setup(
    name="docutrance",              
    version="0.4.0",                       
    author="Jordan Wolfgang Klein",
    author_email="jwklein14@gmail.com",
    description="A short description of your package",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Lone-Wolfgang/multilingual-retriever-for-milton-h-erickson",  
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(), 
    python_requires=">=3.10",
    install_requires= requirements,
    include_package_data=True,            
)