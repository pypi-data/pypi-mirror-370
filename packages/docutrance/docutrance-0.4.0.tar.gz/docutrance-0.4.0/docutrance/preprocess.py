from docutrance.util import compute_relative_diff

from datasets import Dataset
import json
import matplotlib.pyplot as plt
import os
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import spacy_udpipe
from tabulate import tabulate
from tqdm.auto import tqdm
from typing import Callable


class UDSentenceTokenizer:
    """
    Manages and caches multiple UDPipe-based spaCy tokenizers for multilingual processing.

    This class allows efficient switching between tokenizers for different languages
    by preloading them into memory. It is particularly useful when working with
    multilingual datasets where sentence segmentation or tokenization is needed
    in multiple languages.

    Parameters:
        languages (list of str): List of ISO 639-1/2 language codes supported by spacy-udpipe.
                                 Each model will be downloaded (if not already present) and loaded.

    Example:
        manager = UDTokenizerManager(['en', 'fr', 'de'])
        sentences = manager.tokenize('fr', "Bonjour. Comment ça va ?")

    Methods:
        tokenize(lang, text):
            Tokenizes and segments the given text into sentences using the language-specific model.
            Returns a list of sentence strings.
    """
    def __init__(self, languages):
        self.models = {}
        print(f"Initializing UD Tokenizer for {languages}. . .")
        for lang in languages:
            spacy_udpipe.download(lang)  
            self.models[lang] = spacy_udpipe.load(lang)
    
    def tokenize(self, lang, text):
        """
        Tokenizes and segments the input text using the tokenizer for the specified language.

        Parameters:
            lang (str): The language code (e.g., 'en', 'fr') corresponding to the desired tokenizer.
            text (str): The text to be tokenized and segmented into sentences.

        Returns:
            list of str: A list of sentences as segmented by the language model.

        Raises:
            ValueError: If the specified language model is not loaded.
        """
        nlp = self.models.get(lang)
        if not nlp:
            raise ValueError(f"Language model for '{lang}' not loaded.")
        return [sent.text for sent in nlp(text).sents]


def align_sentences(
    source_sentences: list[str],
    target_sentences: list[str],
    model: SentenceTransformer
) -> dict:
    """
    Align source and target sentences using sentence embeddings and cosine similarity.
    """

    embed = lambda sentences: model.encode(sentences, convert_to_tensor=True)
    source_embeddings = embed(source_sentences)
    target_embeddings = embed(target_sentences)

    # Compute cosine similarity matrix
    similarity_matrix = cos_sim(source_embeddings, target_embeddings)

    best_matches = []
    best_scores = []

    for _, row in enumerate(similarity_matrix):
        best_match_idx = row.argmax().item()
        best_score = row[best_match_idx].item()
        best_matches.append(target_sentences[best_match_idx])
        best_scores.append(best_score)

    return {
        "source": source_sentences,
        "target": best_matches,
        "score": best_scores
    }

def align_core_competencies(
    io_paths: dict[str],
    model: SentenceTransformer,
    source_language: tuple = ('en', 'english'),
    target_languages: list = ['es', 'fr', 'it', 'pt']
):
    """
    Aligns sentence pairs between a source language and multiple target languages
    using a sentence transformer model. Tokenizes text, computes semantic similarity, 
    and saves results to Parquet files.

    Parameters:
        io_paths: Dictionary of input/output paths including 'corpus' and 'output'.
        model: SentenceTransformer used for sentence alignment.
        source_language: Tuple of (language code, name) for the source language.
        target_languages: List of language codes to align with the source.

    Returns:
        None. Outputs saved to disk.
    """
    source, name = source_language
    tokenizer = UDSentenceTokenizer([source] + target_languages)

    # Step 1: Prepare output paths
    io_paths["intermediate"] = Path.cwd() / "intermediate"
    os.makedirs(io_paths["intermediate"], exist_ok=True)
    io_paths["files"] = []

    # Step 2: Load corpus
    corpus = json.loads(Path(io_paths["corpus"]).read_text(encoding='utf-8'))

    # Step 3: Prepare list of all (section_id, target_language) pairs to process
    tasks = [
        (section_id, target)
        for section_id, entry in corpus.items()
        for target in target_languages
        if target in entry
    ]

    # Step 4: Process 
    for section_id, target in tqdm(tasks, desc="Aligning sections"):
        output_path = Path(io_paths["intermediate"]) / f"{section_id}-{source}-{target}.parquet"
        io_paths["files"].append(output_path)

        if output_path.exists():
            continue

        entry = corpus[section_id]
        tokenize = lambda lang: tokenizer.tokenize(lang, entry[lang]["content"])

        sentences = {
            "source": tokenize(source),
            "target": tokenize(target),
        }

        headers = {
            "source": entry[source]["header"],
            "target": entry[target]["header"]
        }

        result = align_sentences(sentences["source"], sentences["target"], model)

        output = pd.DataFrame({
            "section_id": section_id,
            "target_language": target,
            f"{name}_header": headers["source"],
            f"{name}_sentence": result["source"],
            f"non_{name}_header": headers["target"],
            f"non_{name}_sentence": result["target"],
            "similarity_score": result["score"]
        })

        output.to_parquet(output_path)

    # Step 5: Merge intermediate files
    final_output = pd.concat(
        [pd.read_parquet(file) for file in io_paths["files"]]
    ).reset_index(drop=True)
    os.makedirs(os.path.dirname(io_paths["output"]), exist_ok=True)
    final_output.to_parquet(io_paths["output"])
    print(f"Combined intermediate outputs. Saved to {io_paths['output']}")

def preprocess_core_competencies(
        df: pd.DataFrame,
        model: SentenceTransformer=None,
        filters: list[Callable[[pd.DataFrame], pd.Series]] = None,
        remove_intermediate_columns: bool = True,
        repo_id: str = None
):
    """
    Prepares aligned sentence pairs for analysis by removing duplicates, 
    applying filters, adding token-based features, and assigning sentence IDs.

    Parameters:
        df: Input DataFrame of aligned sentence pairs.
        model: Optional transformer model for tokenization.
        filters: Optional list of filter functions to apply.
        remove_intermediate_columns: Whether to drop helper columns.
        repo_id: Optional HuggingFace Hub repo to push the final dataset.

    Returns:
        Processed DataFrame.
    """
    original_columns = list(df.columns)
    results = df.copy()

    # 1. Sort by score, staging dataset for deduplication.
    results.sort_values('similarity_score', ascending=False, inplace=True)

    # 2. Drop duplicates from each [{language}, {sentence}] subsets, keeping the highest scores
    for column in ["english_sentence", "non_english_sentence"]:
        results.drop_duplicates(subset=['target_language', column], inplace=True)

    # 3. Add columns with word lists and token lists
    for column in ["english_sentence", "non_english_sentence"]:
        name = lambda suffix: column.replace('sentence', suffix)
        results[name('words')] = results[column].apply(lambda x: x.split())
        if model:
            results[name('tokens')] = results[column].apply(lambda x: model.tokenizer.tokenize(x))

    # 4. Add relative length difference
    results['relative_len_diff'] = results.apply(
        lambda row: compute_relative_diff(
            len(row['english_words']), 
            len(row['non_english_words'])
        ),
        axis=1
    )

    # 5. Apply filters (if any)
    if filters:
        mask = pd.Series(True, index=results.index)
        for condition in filters:
            mask &= condition(results)
        results = results[mask]
    
    # 6. Assign a sentence_id to every unique ['section_id', 'english_sentence']
    results = results.sort_index().reset_index(drop=True)
    sentence_ids = pd.DataFrame()
    for section_id, subset in results[['section_id', 'english_sentence']].drop_duplicates().groupby('section_id'):
        subset = subset.reset_index(drop=True)
        subset['sentence_id'] = subset.index.map(lambda i: f"{section_id}-{str(i).zfill(3)}")
        sentence_ids = pd.concat([sentence_ids, subset])

    results = results.merge(sentence_ids, how='left', on=['section_id', 'english_sentence'])
    original_columns = ['sentence_id'] + original_columns

    # 7. After processing, remove columns with token lists and length difference metrics
    if remove_intermediate_columns:
        results = results[original_columns]

    # 8. If a repo id is provided, push the preprocessed dataset to HuggingFace Hub
    if repo_id:
        Dataset.from_pandas(results).push_to_hub(repo_id)
    return results

def analyze_len_difference_vs_similarity(
        df: pd.DataFrame,
        thresholds: list = [n * 0.1 for n in range(10, 0, -1)],
        x_column = "relative_len_diff",
        y_column = "similarity_score",
        figsize = (6, 3)
):
    """
    Prepares a summmary table and plot showing how similarity score and /
    data retention change  over progressively stricter maximium length /
    difference thresholds.
    """
    
    def summarize(df):
        """Iterates through thresholds, computes mean score and data retention."""
        # Initiate an empty list of rows for the final summary table
        rows = []

        # First row: Baseline stats for the whole dataset
        overall_avg = df[y_column].mean()
        rows.append({
            "Max Relative Len Diff": "-",
            "Avg Similarity": round(overall_avg, 4),
            "Data Retained (%)": 100.00
        })

        # Remaining rows: Threshold-based stats
        total_rows = len(df)
        for threshold in thresholds:
            filtered = df[df[x_column] < threshold]
            avg_similarity = filtered[y_column].mean()
            retention = len(filtered) / total_rows * 100  

            rows.append({
                "Max Relative Len Diff": round(threshold, 2),
                "Avg Similarity": round(avg_similarity, 4),
                "Data Retained (%)": round(retention, 2)
            })

        summary = pd.DataFrame(rows)
        return summary 

    def plot(summary):
        """Produces a line plot from the summary table."""

        plot_data = summary[summary["Max Relative Len Diff"] != "-"]


        plt.figure(figsize=figsize)
        plt.plot(
            plot_data['Max Relative Len Diff'],
            plot_data['Avg Similarity'],
            marker='o',
            color='blue',
            linewidth=2
        )
        plt.title('Average Similarity vs. Max Relative Length Difference')
        plt.xlabel('Relative Len Difference Threshold')
        plt.ylabel('Average Similarity')
        plt.grid(True)
        plt.gca().invert_xaxis()
        plt.tight_layout()
        plt.show()
    
    df = preprocess_core_competencies(df, remove_intermediate_columns=False)
    summary = summarize(df)
    plot(summary)
    print(tabulate(summary, headers='keys', tablefmt='github', showindex=False))
    