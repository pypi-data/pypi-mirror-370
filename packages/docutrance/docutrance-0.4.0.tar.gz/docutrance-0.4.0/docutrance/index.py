from bs4 import BeautifulSoup
from deepdiff import DeepDiff
import fitz
from opensearchpy import OpenSearch
import os
import pandas as pd
from pathlib import Path
import requests
import sentence_transformers
import spacy
from typing import List, Callable, Optional, Tuple
import spacy.lang
from tqdm.auto import tqdm
from urllib.parse import urlparse
import json
from pathlib import Path
import re

from docutrance.util import (
    lemmatize,
    load_text,
    get_files
)

class CollectedWorksHandler:

    def __init__(
        self,
        raw_data_dir: str,
        output_path: str,
        **kwargs
    ):
    
        self.input = raw_data_dir
        self.output = output_path
        self.init_documents(**kwargs)
        self.init_paragraphs()


    def check_paths(self):
        if not os.path.isdir(self.input):
            raise ValueError("Please select path to a directory where raw data is saved")
        if Path(self.output).stem == ".parquet":
            raise ValueError("Please selected an output file with .parquet suffix to save preprocessed document.")
    
    def get_title_and_author(self, file: Path) -> dict:
        """Extract title and author from PDF metadata."""
        doc = fitz.open(file)
        metadata = doc.metadata
        return {
            "title": metadata["title"],
            "author": metadata["author"].split(', ')
        }

    def get_body(self, file: Path) -> dict:
        """Extract full text body from a file."""
        return {
            "body": load_text(file)
        }

    def parse_file_name(self, file: Path) -> dict:
        """Parse metadata from structured file name."""
        parts = file.stem.split('-')
        volume = int(parts[0][-2:])
        order = int(parts[1])
        section = int(parts[2][-2:])
        chapter = (
            "Introduction" if parts[3] == 'Intro' else
            "References" if parts[3] == "References" else
            f"Chapter {int(parts[3][-2:])}"
        )
        return {
            "volume": volume,
            "order": order,
            "section": section,
            "chapter": chapter,
            "document_id": f"{str(volume).zfill(2)}-{str(order).zfill(3)}"
        }
    
    def clean_body(self, text):
        """Split text into cleaned paragraphs of minimum length."""

        paragraphs = text.split('\n\n')
    
        for character in ['_', '*']:
            paragraphs = [p.replace(character, '') for p in paragraphs]
        
        paragraphs = [p.replace("\n", " ") for p in paragraphs]
        
        output='\n'.join(paragraphs)
        return output

    def init_documents(self, **kwargs) -> pd.DataFrame:
        """Create or load a document metadata index."""

        if os.path.exists(self.output) and not kwargs.get("restart"):
            df = pd.read_parquet(self.output)
            print(f"Loaded index dataframe from {self.output}")
            self.documents = df
            return

        files = get_files(self.input)
        rows = []
        for file in tqdm(files, desc='Building index dataframe'):
            row = {"file": file.stem}
            for fn in [self.get_title_and_author, self.get_body, self.parse_file_name]:
                row.update(fn(file))
            row.update({"body": self.clean_body(row["body"])})
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_parquet(self.output)
        print(f"Saved index dataframe to {self.output}")
        self.documents = df
        return

    def init_paragraphs(self) -> pd.DataFrame:
        df = self.documents.copy()
        df['paragraph'] = df.body.apply(lambda x: x.split('\n'))
        df =df.explode('paragraph', ignore_index=True)
        self.paragraphs = df
        return
    


class PdfHandler:

    def __init__(
        self,
        input_path: str,
        title: str,
        document_id: str,
        output_path: str,
        content_map: list[tuple],
        **kwargs
    ):
        self.input = input_path
        self.title = title
        self.document_id = document_id
        self.output = output_path
        self.content_map = content_map or []
        self.preprocess(**kwargs)

    def handle_paths(self):
        if not Path(self.input).suffix.lower() == '.pdf':
            raise ValueError(f"Input {self.input} is not a valid pdf.")
        if not Path(self.output).suffix.lower() == '.parquet':
            raise ValueError(f"Output {self.output} is not a valid parquet path.")
        os.makedirs(os.path.dirname(self.output), exist_ok=True)

    def get_section_label(self, page_num: int):
        for page_range, label in self.content_map:
            if page_num in page_range:
                return label
        return "unknown"

    def clean_pdf_text(self, text: str) -> str:
        """
        Clean PDF text minimally so words are preserved exactly
        as they appear in the PDF for reliable highlight matching.
        """
        # Normalize carriage returns
        text = text.replace("\r", "\n")
        # Remove soft hyphens (U+00AD) that break words visually
        text = text.replace("\u00ad", "")
        # Keep all newlines; only collapse excessive spaces (not touching newlines)
        text = re.sub(r'[ ]{2,}', ' ', text)
        return text.strip()

    def extract_text_blocks(self) -> pd.DataFrame:
        """
        Extract text in blocks while preserving word boundaries and layout.
        """
        print(f"Building dataframe from {self.input}")
        self.handle_paths()

        doc = fitz.open(self.input)
        page_nums = list(range(len(doc)))
        records = []

        for page_idx in tqdm(page_nums, desc="Extracting text blocks"):
            try:
                page = doc.load_page(page_idx)
                page_num = page_idx + 1  # 1-based page numbering
                section = self.get_section_label(page_num)

                page_dict = page.get_text("dict")

                for block in page_dict["blocks"]:
                    if "lines" not in block:
                        continue  # skip images or non-text blocks

                    block_text_lines = []
                    for line in block["lines"]:
                        # Join all spans in the line
                        line_text = "".join(span["text"] for span in line["spans"])
                        line_text = self.clean_pdf_text(line_text)
                        block_text_lines.append(line_text)

                    block_text = "\n".join(block_text_lines)
                    if block_text.strip():
                        records.append({
                            "file": self.input,
                            "title": self.title,
                            "document_id": f"{self.document_id}-{str(page_num).zfill(3)}",
                            "page_num": page_num,
                            "bbox": tuple(block["bbox"]),
                            "text": block_text,
                            "section": section
                        })

            except Exception as e:
                print(f"Error on page {page_num}: {e}")

        df = pd.DataFrame.from_records(records)
        df.to_parquet(self.output)
        self.extracted = df
        print(f"Document dataframe initiated. Saved to {self.output}")

    def get_paragraphs(self, **kwargs):
        df = self.extracted.copy()
        tqdm.pandas(desc="Filtering underlength text blocks.")
        min_length = kwargs.get("min_length", 16)
        df = df[df.text.apply(lambda x: len(x.split()) >= min_length)]
        df.rename(columns={"text": "paragraph"}, inplace=True)
        self.paragraphs = df.reset_index(drop=True)

    def combine_text_blocks(self, **kwargs):
        df = self.extracted.copy()
        df = df.groupby(["file", "title", "document_id", "section", "page_num"]).agg({
            "text": lambda x: "\n\n".join(list(x))
        })
        df.reset_index(inplace=True)
        self.documents = df

    def preprocess(self, **kwargs):
        if not os.path.exists(self.output) or kwargs.get("restart"):
            self.extract_text_blocks()
        else:
            self.extracted = pd.read_parquet(self.output)
            print(f"Loaded documents from {self.output}")
        self.get_paragraphs()
        self.combine_text_blocks()

class PdfCorpusHandler:
    def __init__(self, *pdf_handlers: 'PdfHandler'):
        self.pdf_handlers = pdf_handlers
        self.combine_documents()
        self.combine_paragraphs()

    def combine_documents(self):
        self.documents = pd.concat(
            [handler.documents for handler in self.pdf_handlers if hasattr(handler, 'documents')],
            ignore_index=True
        )
    
    def combine_paragraphs(self):
        self.paragraphs = pd.concat(
            [handler.paragraphs for handler in self.pdf_handlers if hasattr(handler, 'paragraphs')],
            ignore_index=True
        )


class DocumentPreprocessor:
    def __init__(
        self,
        corpus_handler,
        column_mappings: dict,
        sbert: sentence_transformers.SentenceTransformer,
        spacy: spacy.language.Language
    ):
        self.documents = corpus_handler.documents
        self.paragraphs = corpus_handler.paragraphs
        self.column_mappings=column_mappings
        self.sbert=sbert
        self.spacy=spacy
        self.check_mappings()

    def check_mappings(self):
        methods = ["embedding", "lemmatized"]

        for source, target in self.column_mappings.items():
            if not any(target == f"{source}_{method}" for method in methods):
                raise ValueError(f"Column mapping {source}:{target} is not acceptable. Did you mean {source}_embedding or {source}_lemmatized ?")

    def process_column(
        self,
        source,
        target
    ):
        if target in self.documents.columns:
            print(f"{target} has already been processed. Continuing. . .")
            return
        
        suffix = target.split("_")[-1]
        if suffix=="lemmatized":
            function = lambda x: lemmatize(self.spacy, x)
        elif suffix=="embedding":
            function = lambda x: self.sbert.encode(x)

        tqdm.pandas(desc=f"Processing {target}")
        self.documents[target] = self.documents[source].progress_apply(function)
        return

    def preprocess_documents(self, **kwargs):
        save_as = kwargs.get("save_as")

        for source, target in self.column_mappings.items():
            self.process_column(source, target)
        
        if save_as:

            save = [column for column in self.documents.columns if "embedding" not in column]
            copy = self.documents.copy()[save]
            copy.to_parquet(save_as)
        return self.documents
    
    def get_sentence_boundaries(self, paragraph: str):
        """Return sentence boundary character offsets using spaCy."""
        doc = self.spacy(paragraph)
        sentence_boundaries = list(enumerate([(sent.start_char, sent.end_char) for sent in doc.sents]))
        return sentence_boundaries
    
    def get_segment_boundary(self, offset_mapping: list[tuple]):
        """Get start and stop character offsets for a segment."""
        return offset_mapping[1][0], offset_mapping[-2][1]
    
    def get_segment_boundaries(self, section: str, **kwargs):

        """Return list of segment boundaries based on tokenizer offset mappings."""
        tokenizer = self.sbert.tokenizer
        inputs = tokenizer(
            section,
            truncation=True,
            return_overflowing_tokens=True,
            max_length=kwargs.get("max_length", 128),
            stride=kwargs.get("stride", 96),
            return_attention_mask=False,
            return_token_type_ids=False,
            return_offsets_mapping=True
            )
        
        segment_boundaries = [self.get_segment_boundary(mapping) for mapping in inputs["offset_mapping"]]
        return segment_boundaries
    
    def extract_sentences(self, paragraph, sentence_boundaries):
        sentences = []
        for _, (start, stop) in sentence_boundaries:
            sentences.append(paragraph[start:stop])
        return sentences

    def embed_sentences(self, sentences):
        return [self.sbert.encode(sentence) for sentence in sentences]

    def get_sentences_and_segments(self, row):
        segment_boundaries = row["segment_boundaries"]
        sentence_boundaries = row["sentence_boundaries"]
        all_sentences = row["all_sentences"]
        all_embeddings = row["all_sentence_embeddings"]

        indices = [
            [idx for idx, (start, stop) in sentence_boundaries if start >= segment[0] and stop <= segment[1]]
            for segment in segment_boundaries
        ]

        # Filter out empty index lists
        indices = [i for i in indices if len(i) > 0]
        if not indices:
            return [], [], [], []

        df = pd.DataFrame({"indices": indices})
        df["start"] = df.indices.apply(lambda x: x[0])
        df["stop"] = df.indices.apply(lambda x: x[-1])
        df["len"] = df.apply(lambda x: x.stop - x.start, axis=1)
        df.sort_values('len', ascending=False, inplace=True)
        
        for col in ['start', 'stop']:
            df.drop_duplicates(subset=col, keep='first', inplace=True)

        df.sort_index(inplace=True)

        df["sentences"] = df.apply(lambda x: all_sentences[x.start:x.stop + 1], axis=1)
        df["sentence_embeddings"] = df.apply(lambda x: all_embeddings[x.start:x.stop + 1], axis=1)
        df["segment"] = df.sentences.apply(lambda x: ' '.join(x))
        df["segment_length"] = df.segment.apply(lambda x: len(x.split()))

        return df.sentences.tolist(), df.sentence_embeddings.tolist(), df.segment.tolist(), df.segment_length.to_list()
    
    def preprocess_segments(self, **kwargs):
        """Split documents into segments, align with sentence boundaries, and embed."""
        # Enable tqdm progress bars in pandas

        df = self.paragraphs.copy()

        tqdm.pandas(desc="Getting sentence boundaries")
        df['sentence_boundaries'] = df.paragraph.progress_apply(lambda x: self.get_sentence_boundaries(x))

        tqdm.pandas(desc="Extracting sentences")
        df['all_sentences'] = df.progress_apply(lambda x: self.extract_sentences(x["paragraph"], x["sentence_boundaries"]), axis=1)

        tqdm.pandas(desc="Embedding sentences")
        df["all_sentence_embeddings"] = df.all_sentences.progress_apply(lambda x: self.embed_sentences(x))

        tqdm.pandas(desc="Getting segment boundaries" )        
        df['segment_boundaries'] = df.paragraph.progress_apply(lambda x: self.get_segment_boundaries(x, **kwargs))
        
        tqdm.pandas(desc="Building segments")
        segment_outputs = df.progress_apply(lambda x: self.get_sentences_and_segments(x), axis=1)
        print(segment_outputs)

        # Split the tuple returned by get_sentences_and_segments into separate columns
        df["sentences"] = segment_outputs.apply(lambda x: x[0])
        df["sentence_embeddings"] = segment_outputs.apply(lambda x: x[1])
        df["segment"] = segment_outputs.apply(lambda x: x[2])
        df["segment_length"] = segment_outputs.apply(lambda x: x[3])
        df = df.explode(['segment', 'segment_length', 'sentences', 'sentence_embeddings'])
        df = df.dropna().reset_index(drop=True)

        tqdm.pandas(desc="Embedding segments")
        df["segment_embedding"] = df.segment.progress_apply(lambda x: self.sbert.encode(x))

        tqdm.pandas(desc="Asigning segment ids")
        df["segment_index"] = df.groupby("document_id").cumcount()
        df["segment_id"] = df.progress_apply(lambda x: f"{x.document_id}-{str(x.segment_index).zfill(3)}", axis=1)

        df.drop(columns = ["paragraph", "sentence_boundaries", "all_sentences", "all_sentence_embeddings", "segment_boundaries"], inplace=True)

        self.segments=df
        return self.segments
 
class IngestPipeline:

    def __init__(
        self,
        df: pd.DataFrame,
        client: OpenSearch,
        index: str,
        settings: dict,
        mappings: dict,
        **kwargs
    ):
        self.df = df
        self.client=client
        self.index=index
        self.settings=settings
        self.mappings=mappings
    

    def is_index_different(self) -> bool:
        """Check if an OpenSearch index differs from the expected settings and mappings."""
        
        # Fetch current index settings and mappings
        old_settings = self.client.indices.get_settings(index=self.index)[self.index]["settings"]["index"]
        old_mappings = self.client.indices.get_mapping(index=self.index)[self.index]["mappings"].get("properties", {})

        # Filter out irrelevant settings keys
        relevant_old_settings = {k: old_settings.get(k) for k in self.settings}

        # Compute diffs
        settings_diff = DeepDiff(relevant_old_settings, self.settings, ignore_order=True)
        mappings_diff = DeepDiff(old_mappings, self.mappings, ignore_order=True)

        if settings_diff or mappings_diff:
            print("⚠️ Index configuration mismatch detected. Recreating index...")
            print("Settings diff:", settings_diff)
            print("Mappings diff:", mappings_diff)
            return True
        else:
            print(f"ℹ️ Index '{self.index}' already exists and matches expected configuration.")
            return False
        
    def init_opensearch_index(self, **kwargs):

        body = {
            "settings": self.settings,
            "mappings": self.mappings
        }

        if not self.client.indices.exists(index=self.index):
            print(f"ℹ️ Initiating new index, {self.index}")
            self.client.indices.create(index=self.index, body=body)

        elif kwargs.get('overwrite_old_index') or self.is_index_different():
            self.client.indices.delete(index=self.index)
            print(f"🗑️ Deleted old index '{self.index}'.")
            self.client.indices.create(index=self.index, body=body)
    
        print("Index Configuration:")
        print(json.dumps(body, indent=4))
    
    def ingest(self, id_column, **kwargs):

        """Index documents from a DataFrame into an OpenSearch index."""
        self.init_opensearch_index(**kwargs)
        df = self.df.copy()
        print(df.head())

        print(df.head())

        indexed_count = 0
        rows = [{column: df.loc[idx, column] for column in df.columns} for idx in df.index]
        for row in tqdm(rows, desc = f"Indexing documents to {self.index}"):
            index_kwargs = {
                "index": self.index,
                "id": row[id_column],
                "body": row
            }
            try:
                self.client.index(**index_kwargs)
                indexed_count += 1
            except Exception as e:
                print(f"❌ Failed to index {index_kwargs['id']}: {e}")
        
        if indexed_count:
            print(f"✅ Successfully indexed {indexed_count} documents.")
        else:
            print("⚠️ No documents were indexed.")
        

    


        
        


# def get_wikipedia_content(url: str) -> dict:
#     """Fetch and parse Wikipedia page content."""
#     title = urlparse(url).path.split("/wiki/")[-1]
#     endpoint = f"https://en.wikipedia.org/api/rest_v1/page/html/{title}"
#     headers = {"User-Agent": "WikiScraperBot/1.0"}

#     response = requests.get(endpoint, headers=headers)
#     if response.status_code != 200:
#         print(f"[Error] Failed to fetch '{title}': {response.status_code}")
#         return None

#     html = response.text
#     soup = BeautifulSoup(html, 'html.parser')
#     paragraphs = soup.find_all("p")
#     body = "\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())

#     return {
#         "title": soup.title.get_text() if soup.title else title.replace("_", " "),
#         "body": body
#     }






















# def build_wikipedia_index(
#     urls: list,
#     lemmatizer: spacy,
#     encoder: SentenceTransformer,
#     output_path: str=None
#     ):
#     """Given a list of wikipedia links, extracts and preprocesses data for indexing."""
#     tqdm.pandas(desc= "Extracting data from Wikipedia. ..")

#     df = pd.DataFrame({'url': urls})
#     df['document_id'] = df.index.map(lambda x: str(x).zfill(3))
#     df[['title', 'body']] = df.url.progress_apply(lambda x: pd.Series(get_wikipedia_content(x)))
#     df.dropna(inplace=True)
    
#     tqdm.pandas(desc='Lemmatizing body. . .')
#     df['body_lemmatized'] = df.body.progress_apply(lambda x: lemmatize(lemmatizer, x))

#     tqdm.pandas(desc='Computing title embeddings. . .')
#     df['title_embedding'] = df.title.progress_apply(lambda x: encoder.encode(x))

#     if output_path:
#         df.to_parquet(output_path)
#         print(f'Saved output to {output_path}')
    

#     return df