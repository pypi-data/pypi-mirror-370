from copy import deepcopy

from sentence_transformers import SentenceTransformer, util
from typing import Dict, List
import re
import spacy
import pandas as pd
from opensearchpy import OpenSearch
from typing import Optional
import json

from docutrance.util import lemmatize, remove_stopwords

class QueryProcessor:
    def __init__(
        self,
        user_input: str = None,
        spacy_model: spacy.language.Language = None,
        sbert_model: Optional[SentenceTransformer] = None,
        **kwargs
    ):
        self.user_input = user_input
        self.spacy = spacy_model
        self.sbert = sbert_model

        # Processed features
        self.stripped = None
        self.lemmatized = None
        self.embedding = None
        self.exact_match = None
        self.query_type = "match_all"
        self.debug = True if kwargs.get('debug') else False

        self.preprocess()
        self.debug_statement()

        self.body = self.compose_query_body()

    def __str__(self):
        output = self.as_dict().copy()
        embedding = output.get("embedding")
        if embedding is not None:
            output["embedding"] = f"[{', '.join([str(v) for v in embedding[:3]])}. . .]"
        
    
        return f"Query Type: {self.query_type}\n\n{json.dumps(output, indent=4)}"
    
    def debug_statement(self):
        if self.debug:
            print (f"Debug mode active. Will automatically print queries.")
            print()
            print(self.__str__())


    def preprocess(self):
        if not self.user_input:
            return

        match = re.search(r'"(.*?)"', self.user_input)
        self.exact_match = match.group(1) if match else None
        self.query_type = "keyword" if self.exact_match else "semantic"

        self.user_input = self.user_input.replace('"', '').strip() if self.exact_match else self.user_input
        if self.spacy:
            self.stripped = remove_stopwords(self.spacy, self.user_input)
            self.lemmatized = lemmatize(self.spacy, self.stripped).replace('\n', ' ')

        if self.sbert:
            self.embedding = self.sbert.encode(self.user_input)
    
    def reinit(self, new_input, new_spacy=None, new_sbert=None, **kwargs):
        
        args = (
            new_input,
            new_spacy or self.spacy,
            new_sbert or self.sbert
        )
        kwargs["debug"] = self.debug
        self.__init__(*args, **kwargs)

    def as_dict(self) -> Dict[str, str]:
        output = {}

        if self.user_input is not None:
            output["input"] = self.user_input
        if self.stripped is not None:
            output["stripped"] = self.stripped
        if self.lemmatized is not None:
            output["lemmatized"] = self.lemmatized
        if self.exact_match:
            output["exact_match"] = self.exact_match
        if self.embedding is not None:
            output["embedding"] = self.embedding

        return output
    
    
    def compose_subquery(self, subquery: Dict) -> Dict:
        """
        Composes an OpenSearch subquery using the current Query object's processed data.
        """
        subquery_type = subquery["subquery_type"]
        input_type = subquery["input_type"]
        possible_types = ["knn", "neural", "match", "match_phrase", "multi_match"]

        if subquery_type not in possible_types:
            raise ValueError(f"Unsupported subquery type '{subquery_type}'. Choose from: {possible_types}")
        if input_type not in self.as_dict():
            raise ValueError(f"Input type '{input_type}' not found in query. Available: {list(self.as_dict().keys())}")

        # Determine OpenSearch input key
        if subquery_type == 'knn':
            input_key = 'vector'
        elif subquery_type == 'neural':
            input_key = 'query_text'
        else:
            input_key = 'query'

        input_value = self.as_dict()[input_type]
        input_block = {input_key: input_value}

        # Construct subquery
        if subquery_type == "multi_match":
            output = {subquery_type: {**input_block, **subquery.get("kwargs", {})}}
        else:
            field = subquery.get("field")
            if field is None:
                raise ValueError(f"'field' must be specified for subquery type '{subquery_type}'")
            output = {subquery_type: {field: {**input_block, **subquery.get("kwargs", {})}}}

        return output
    
    def compose_subqueries(self, subqueries: List[Dict]):
        """
        Constructs a list of subqueries based on input and individual subquery parameters.
        """
        subqueries = [self.compose_subquery(subquery) for subquery in subqueries] if self.as_dict() else []
        if len(subqueries) ==1:
            subqueries = subqueries[0]
        return subqueries
    
    def compose_bool_query(
        self,
        should: List[Dict] = [],
        must: List[Dict] = [],
        must_not: List[Dict] = [],
        filter: List[Dict] = []
    ) -> Dict:
        """
        Builds a standard boolean query using 'should' and 'filter' clauses.
        """
        if not any(x for x in [should, must, must_not, filter]):
            return {"query": {"match_all": {}}}

        bool = {
            "query": {
                "bool": {}
            }
        }
        if should:
            bool["query"]["bool"]["should"] = should
        if must:
            bool["query"]["bool"]["must"] = must
        if must_not:
            bool["query"]["bool"]["must_not"] = must_not
        if filter:
            bool["query"]["bool"]["filter"] = filter
        
        return bool
    
    def print_query_body(self, body, subqueries=None, **kwargs):
        copy = deepcopy(body)

        if self.query_type == "semantic" and subqueries:
            key = subqueries[0]["field"]
            value = body["query"]["bool"]["should"]["knn"][key]["vector"]
            
            safe = f"[{', '.join([str(v) for v in value[:3]])}. . .]"
            copy["query"]["bool"]["should"]["knn"][key]["vector"] = safe

        print("\nQuery Body:\n\n")
        print(json.dumps(copy, indent=4))


    
    def compose_query_body(self, **kwargs):
        body = self.compose_bool_query(
                should = self.compose_subqueries(kwargs.get("subqueries", [])),
                must = kwargs.get("must", []),
                must_not = kwargs.get("must_not", []),
                filter = kwargs.get("filter", [])
            )
    
        for key in ['size', 'highlight']:
            value = kwargs.get(key)
            if value is not None:
                body[key] = value
        
        if self.debug:
            self.print_query_body(body, kwargs.get("subqueries"))
        
        return body
    
    
class RetrievalPipeline:
    def __init__(
        self,
        query_processor: QueryProcessor,
        documents: pd.DataFrame,
        client: OpenSearch,
        config: Dict,
        size: int,
        **kwargs
    ):
        
        self.query = query_processor
        self.query.debug = kwargs.get("debug")
        self.documents = documents
        self.client = client
        self.config = config
        self.size = size

    def post_process_response(
        self,
        response: dict,
        column_map: dict=None,
        agg_map: dict=None,
        weight: float=1.0,
        **kwargs
    ):
        """Aggregate and rerank OpenSearch response hits into a grouped DataFrame."""

        k = kwargs.get('k', 60)
        group_column = kwargs.get("group_column", "document_id")
        agg_map = agg_map or {'_score': 'sum'}

        rows = []
        hits = response["hits"]["hits"]
        if not hits:
            return pd.DataFrame()

        for hit in hits:
            row = hit['_source'].copy()
            row['_id'] = hit['_id']
            if '_score' in hit.keys():
                row['_score'] = hit['_score']
            if 'highlight' in hit.keys():
                for column in hit['highlight']:
                    row[f'{column}_highlight'] =hit['highlight'][column]
            rows.append(row)

        df = pd.DataFrame(rows)
        if df.empty:
            return df
        
        if column_map:
            df.rename(columns=column_map, inplace=True)
        
        if '_score' not in df.columns:
            return df
        
        if group_column not in df.columns:
            raise ValueError(f"Group column {group_column} not found in response.")

        agg_map = {k:v for k,v in agg_map.items() if k in df.columns}
        result = df.groupby(group_column).agg(agg_map).reset_index() if agg_map else df
        result['rank'] = result._score.rank(method='first', ascending=False)
        result['rrf'] = weight / (k + result["rank"])

        return result

    def select_highlights(
        self,
        row, 
        **kwargs
        ):
        """Select top highlights from available highlight fields in a result row."""
        n_highlights = kwargs.get("n_highlights", 1)
        
        if self.query.query_type == "keyword":
            highlight_column = kwargs.get("highlight_column", "highlights")
            highlights = row.get(highlight_column)
            if highlights:
                highlights=highlights[:n_highlights][0]
            return highlights


        elif self.query.query_type == "semantic":
            default_columns = {
                "segment": "segment",
                "sentences": "sentences",
                "sentence_embeddings": "sentence_embeddings"
            }
            columns = {**default_columns, **kwargs.get("column_map", {})}
            tag = kwargs.get("tag", "**")

            # Extract values
            segment = row[columns["segment"]]
            sentences = row[columns["sentences"]]
            sentence_embeddings = row[columns["sentence_embeddings"]]

            if not isinstance(sentence_embeddings, (list, tuple)) or len(sentences) != len(sentence_embeddings):
                return segment  # fallback: return the original segment if mismatched

            if not sentence_embeddings or len(sentences) != len(sentence_embeddings):
                return segment  # fallback: return the original segment if mismatched

            # Compute cosine similarity using sentence-transformers
            similarities = util.cos_sim(self.query.embedding, sentence_embeddings)[0]  # shape: (num_sentences,)

            # Get top-N indices
            top_indices = similarities.argsort(descending=True)[:n_highlights]

            # Encapsulate top matching sentences
            for i in top_indices:
                sent = sentences[i]
                highlights = segment.replace(sent, f"{tag}{sent}{tag}", 1)

            return highlights

    def combine_responses(
        self,
        responses: list[pd.DataFrame],
        **kwargs
    ):
        """Merge multiple reranked responses and enrich with document metadata."""
        df = pd.concat(responses)
        if 'rrf' not in df.columns:
            return df
        
        agg_map = {
            **{"rrf": "sum"},
            **{
                column: lambda series: next((x for x in series if x), None) 
                for column in df.columns if column not in ["rank", "document_id"]
            }
        }
        df = df.groupby('document_id').agg(agg_map)
        df['rank'] = df.rrf.rank(method='first', ascending=False)
        df = df.drop(columns='rrf').sort_values('rank').reset_index()
        df['highlights'] = df.apply(lambda x: self.select_highlights(x, **kwargs), axis=1)

        return df.merge(self.documents, how='left', on='document_id')
    
    def retrieve(
        self,
        new_input=None,
        **kwargs
    ):
        if new_input:
            self.query.reinit(new_input)
        tasks = self.config[self.query.query_type]

        responses = []
        for task in tasks:
            index = task["index"]
            column_map = task.get("column_map", {})
            search_kwargs = task.get("search_kwargs", {})
            agg_map = task.get("agg_map", {})
            weight = task.get("weight", 1)

            for bool_key in ["must", "must_not", "filter"]:
                if bool_key in kwargs:
                    search_kwargs[bool_key] = kwargs[bool_key]


            body = self.query.compose_query_body(**search_kwargs)
            response = self.client.search(body=body, index=index, size=self.size)
            responses.append(self.post_process_response(
                response,
                column_map=column_map, 
                agg_map=agg_map, 
                weight=weight, 
                **kwargs
                ))
        
        result = self.combine_responses(responses, **kwargs)
        return result





