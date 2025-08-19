from typing import Union, List
from pathlib import Path

import pymupdf4llm
from typing import Optional
import deepl
import time
from opensearchpy import OpenSearch
import spacy
import pandas as pd

class DfLoader:

    def __init__(
        self,
        input_path: str,
        verbose: bool=True,
        **kwargs
    ):
        self.input = Path(input_path)
        self.verbose = verbose
        self.output_type = kwargs.get("output_type", "pandas")

    
    def load(self, **kwargs):
        if self.input.suffix == ".parquet":
            method = pd.read_parquet
        elif self.input.suffix == ".xlsx":
            method = pd.read_excel
        elif self.input.suffix == '.csv':
            method = pd.read_csv
        
        df = method(self.input, **kwargs)
        if self.verbose:
            print(f"Loaded {self.output_type} dataframe from {self.input}")
            print()
            print("Height:")
            print(len(df))
            print()
            print("Columns:")
            print(df.dtypes)
            print()
            print(df.head(5))
        return df

def lemmatize(model: spacy, text: str) -> str:
    """Lemmatize text and remove stopwords."""
    text = text.strip().lower()
    doc = model(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop and token.lemma_ != "-PRON-"])

def remove_stopwords(model: spacy, text: str) -> str:
    """Remove stopwords from text"""
    doc = model(text)
    return " ".join([str(token) for token in doc if not token.is_stop])

def compute_relative_diff(value1, value2):
    """Normalizes the difference between two values by dividing by the mean value."""
    return abs(value1 - value2) / ((value1 + value2) / 2) if (value1 + value2) != 0 else 0


def get_opensearch_client(opensearch_host):
    """Create OpenSearch client"""
    return OpenSearch(hosts=[opensearch_host])


def get_files(root: Union[Path, str], extension: str = '') -> List[Path]:
    """Get all files with given extension"""
    files = sorted([file for file in Path(root).rglob(f'*{extension}') if file.is_file()])
    return files

def load_text(file: Path) -> Optional[str]:
    """Read and convert file content to text"""
    file = Path(file)
    try:
        if file.suffix == '.pdf':
            text = pymupdf4llm.to_markdown(file).strip()
        elif file.suffix in ['.txt', '.text']:
            text = file.read_text(encoding='utf-8').strip()
        # elif file.suffix == '.docx':
        #     text = pypandoc.convert_file(str(file), 'md').strip()
        else:
            text = None
    except Exception as e:
        print(f"Error loading {file.name}: {e}")
        return None
    return text



def translate_fn(translator: deepl.Translator, text, target_lang, retries=3, wait=5):
    for attempt in range(retries):
        try:
            result = translator.translate_text(text=text, source_lang='en', target_lang=target_lang.upper())
            return result.text
        except Exception as e:
            print(f"[{target_lang}] Error: {e} | Attempt {attempt + 1} of {retries}")
            time.sleep(wait)
    print(f"Translation failed for '{text}' in '{target_lang}'. Skipping.")
    return None

