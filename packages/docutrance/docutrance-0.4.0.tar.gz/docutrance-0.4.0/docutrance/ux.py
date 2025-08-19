from opensearchpy import OpenSearch
import pandas as pd
from pathlib import Path

import streamlit as st
import spacy
import sentence_transformers
from docutrance.search import (
    QueryProcessor,
    RetrievalPipeline
)

from itertools import product
import json
import fitz

from typing import List
import numpy as np
import webbrowser
from rapidfuzz import fuzz, process
import re
import os
from fitz import TEXT_DEHYPHENATE

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options

class Filter:

    def __init__(
        self,
        field: str,
        client: OpenSearch,
        index: str,
        **kwargs
        ):

        self.field = field
        self.index = index
        self.client = client
        self.options = self.retrieve_options()
        self.key = self.get_session_state_key(**kwargs)
        self.label = self.get_label(**kwargs)

    def retrieve_options(self):
        body = {
            "size": 0,
            "aggs": {
                self.field: {
                    "terms": {
                        "field": self.field,
                        "size": 200
                    }
                }
            }
        }
        
        result = self.client.search(index=self.index, body=body)["aggregations"]
        values = sorted([r["key"] for r in result[self.field]["buckets"]])
        return values
    
    def get_session_state_key(self, **kwargs):
        return kwargs.get("key", f"selected_{self.field}")
    
    def get_label(self, **kwargs):
        return kwargs.get("label", self.field)

    def as_dict(self):
        return {
            "label": self.label,
            "options": self.options,
            "key": self.key
        }
    
class Formatter:
    def __init__(
        self
    ):
        pass

    def format_hit(self, hit):
        pass
    
    def render_results(self, **kwargs):
        pass

class CollectedWorksFormatter(Formatter):

    def __init__(
        self
    ):
        pass

    def format_hit(self, hit):
        """Format author and document metadata into a readable string."""

        author = hit.get('author')
        volume = hit.get('volume')
        section = hit.get('section')
        chapter = hit.get('chapter')
        title = hit.get('title')
        summary = hit.get('summary')
        highlight_data = hit.get('highlights')
        highlights=None

        volume = f"Volume {volume}"
        metadata = [volume]
        if section:
            metadata.append(f"Section {section}")
        if chapter:
            metadata.append(chapter)

        metadata = f'*{", ".join(metadata)}*'
        title = f'### {title}'

        if summary:
            summary = f"*{summary}*"

        if isinstance(author, np.ndarray):
            author = [a for a in author.tolist() if a and a.strip()]
            if author:
                author = ', '.join(author)
                metadata = f'**{author}** | {metadata}'
        
        if isinstance(highlight_data, str):
            highlight_data = [highlight_data]
        
        if isinstance(highlight_data, list):
            highlights = ' '.join(f">{h}" for h in [h.replace('\n', ' ') for h in highlight_data])

        return title, metadata, summary, highlights
    
    def render_results(self, **kwargs):
        results = st.session_state.results.copy()

        page = st.session_state.page_number
        page_size = kwargs.get("page_size", 10)
        total_hits = len(results)

        if results.empty:
            st.warning("No results found.")

        offset = (page - 1) * page_size
        page_hits = results.iloc[offset : page * page_size]
        st.markdown(f"### Showing page {page} of {((total_hits - 1) // page_size) + 1}")

        for _, hit in page_hits.iterrows():
            title, metadata, summary, highlights = self.format_hit(hit)
            

            st.markdown (title)
            st.markdown (metadata)
            if summary:
                st.markdown(summary)
            if highlights:
                st.markdown(highlights)
            st.markdown("---")

class PdfFormatter(Formatter):

    def __init__(self):
        pass

    def format_hit(self, hit):
        """Formats search hits for display in Streamlit."""
        if hit["section"] != "unknown":
            title = f'### {hit["section"]}'
            metadata = f'**{hit["title"]}** | *page {hit["page_num"]}*'
        else:
            title = f"### {hit['title']}"
            metadata = f"*page {hit['page_num']}*"

        formatted = f"{title}\n{metadata}"
        highlights = hit.get('highlights')

        if isinstance(highlights, str):
            highlights = [highlights]

        if isinstance(highlights, list):
            formatted += "\n"
            formatted += ' '.join(
                f">{h}"
                for h in [h.replace('\n', ' ') for h in highlights]
            )

        return formatted, [h.replace('*', '') for h in highlights] if highlights else None

    def highlight_document(self, file, page_num, highlight_data, tmp_path="tmp.pdf"):
        doc = fitz.open(file)
        page = doc[page_num - 1]

        if isinstance(highlight_data, str):
            highlight_data = [highlight_data]

        for highlight in highlight_data:
            queries = [q.strip().replace('*', '') for q in re.split("\n|-", highlight) if q.strip()]
            for q in queries:
                rects = page.search_for(q, flags=TEXT_DEHYPHENATE)
                if rects:
                    for r in rects:
                        annot = page.add_highlight_annot(r)
                        # Set lighter yellow color (RGB normalized to 0-1)
                        annot.set_colors(stroke=(1, 1, 0))  # yellow border
                        annot.set_opacity(0.3)  # 30% opacity for lighter highlight
                        annot.update()

        single_page_doc = fitz.open()
        single_page_doc.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)
        single_page_doc.save(tmp_path, garbage=4, deflate=True)

        doc.close()
        single_page_doc.close()
        return tmp_path
    def file_to_url(self, file, page_num):
        pdf_path = Path(file).resolve().as_posix()
        return f"file:///{pdf_path}#page={page_num}"

    def retrieve_highlighted_document(self, file, page_num, highlight_data, **kwargs):
        tmp_path = self.highlight_document(
            file,
            page_num,
            highlight_data,
            **kwargs
        )
        url = self.file_to_url(tmp_path, page_num)
        webbrowser.open(url)

    def render_results(self, **kwargs):
        results = st.session_state.results.copy()
        page = st.session_state.page_number
        page_size = kwargs.get("page_size", 10)
        total_hits = len(results)

        if results.empty:
            st.warning("No results found.")

        offset = (page - 1) * page_size
        page_hits = results.iloc[offset: page * page_size]
        st.markdown(f"### Showing page {page} of {((total_hits - 1) // page_size) + 1}")

        for _, hit in page_hits.iterrows():
            formatted, highlights = self.format_hit(hit)
            st.markdown(formatted)
            if hit.get("highlights"):
                file, page_num, highlight_data = hit["file"], hit["page_num"], hit["highlights"]
                st.button(
                    label="Retrieve",
                    key=hit["document_id"],
                    on_click=self.retrieve_highlighted_document,
                    args=(file, page_num, highlight_data)
                )
            st.markdown("---")
        
class Docutrance:

    def __init__(
        self,
        retrieval_pipeline: RetrievalPipeline,
        filters: List[Filter],
        formatter: Formatter,
        **kwargs
    ):
        self.pipeline = retrieval_pipeline
        self.filters = filters
        self.formatter = formatter

        self.initial_state = self.get_initial_session_state()
        self.banner = kwargs.get("banner")

        self.setup_page(**kwargs)
        self.initialize_session_state()
        self.render_sidebar(**kwargs)
        self.render_main_input(**kwargs)
    
    def get_initial_session_state(self):
        initial_state = {
            **{
                "user_input": "",
                "page_number": 1,
                "reset_triggered": False,
                "results": self.pipeline.documents
            },
            **{f.key: [] for f in self.filters}
        }

        print(json.dumps({k:v for k,v in initial_state.items() if k!="results"}))
        return initial_state
    
    def initialize_session_state(self, reinit=False):
        """
        Sets up session state on first load.  Client & hybrid-pipeline
        registration only happen once.
        """
        for key, value in self.initial_state.items():
            if reinit or key not in st.session_state:
                st.session_state[key] = value
        
        # self.pipeline.query.reinit(st.session_state.user_input)
        
    def setup_page(self, **kwargs):
        """
        Sets page configuration and title.
        """
        page_title = kwargs.get("page_title", "Document Search")
        title = kwargs.get("title", page_title)
        layout = kwargs.get("layout", "wide")

        st.set_page_config(page_title=page_title, layout=layout)
        st.title(title)
        return
        
    def render_title(self, **kwargs):
        sidebar_title = kwargs.get("sidebar_title", "### 🎯 Refine Your Search")
        sidebar_caption = kwargs.get("sidebar_caption", "Use the filters below to narrow down your results.")


        st.sidebar.markdown(sidebar_title)
        st.sidebar.caption(sidebar_caption)
    
    def render_reset_button(self, **kwargs):
        label = kwargs.get("reset_label", "🔄 Reset")
        type = kwargs.get("reset_button_type", "secondary")

        reset_button = st.sidebar.button(label, type=type)
        if reset_button:
            self.initialize_session_state(reinit=True)
            st.rerun()

            
            
    def render_multiselect_filters(self):
        for filter in self.filters:
           st.sidebar.multiselect(
            label=filter.label,
            options=filter.options,
            key=filter.key
        )
    
    def render_page_control(self, **kwargs):
        title = kwargs.get("page_control_title", "### 📄 Page Navigation")

        st.sidebar.markdown(title)
        if st.sidebar.button("⬅️ Previous") and st.session_state.page_number > 1:
            st.session_state.page_number -= 1
        if st.sidebar.button("➡️ Next"):
            st.session_state.page_number += 1
        
        label = kwargs.get("page_input_label", "Jump to page")
        page_input = st.sidebar.text_input(label, value=str(st.session_state.page_number))

        if page_input.isdigit():
            st.session_state.page_number = max(1, int(page_input))
    
    def render_sidebar(self, **kwargs):
        """
        Renders sidebar filters, reset and pagination controls.
        """
        if self.banner:
            st.sidebar.image(self.banner, use_container_width=True)
        self.render_title(**kwargs)
        self.render_reset_button(**kwargs)
        self.render_multiselect_filters()

        st.sidebar.markdown("---")

        self.render_page_control(**kwargs)

    def render_main_input(self, **kwargs):
        label = kwargs.get("search_bar_label", "Enter your search query")
        placeholder = kwargs.get("search_bar_placeholder", "Search documents. . .")
        key = "user_input"

        st.text_input(
            label,
            key=key,
            value=st.session_state.get(key, ""),
            placeholder=placeholder
        )
            
    def compose_must_subquery(self):

        must = []
        for field, key in zip (
            [f.field for f in self.filters],
            [f.key for f in self.filters]
        ):
            value = st.session_state.get(key, [])
            if value:
                value = value if isinstance(value, list) else [value]
                must.append({"terms": {field: value}})
        return must
    
    def get_results(self, **kwargs):
        if st.session_state.user_input != self.pipeline.query.user_input:
            self.pipeline.query.reinit(st.session_state.user_input)

        st.session_state.results = self.pipeline.retrieve(
            must=self.compose_must_subquery()
            )
        
    
    def print_session_state(self):
        state = st.session_state.to_dict()
        print("Session State:")
        print()
        print(json.dumps({k:v for k,v in state.items() if k != "results"}, indent=4))
        print()
    
    def retrieve(self, **kwargs):
        self.get_results()
        self.formatter.render_results(**kwargs)

    
