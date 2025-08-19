from openai import OpenAI
import pandas as pd
import tiktoken
import json

class KeywordExtractor:

    def __init__(
        self,
        client: OpenAI,
        documents: pd.DataFrame,
        model_name: str,
        keywords: list[str],
        template: str
    ):
        self.client = client
        self.documents = documents
        self.preprocessed = None
        self.model_name = model_name
        self.keywords = '\n'.join(keywords)
        self.template = template
        self.encoder = self.get_encoder()
        self.base_length = self.get_base_template_length()

    def get_encoder(self):
        get_ = lambda name: tiktoken.get_encoding(name)

        model_to_encoder = tiktoken.model.MODEL_TO_ENCODING
        if self.model_name not in model_to_encoder.keys():
            print(f"{self.model_name} is not supported by tiktoken. Using default encoder, 'o200k_base'")
            self.encoder = get_('o200k_base')
            return
        
        encoder = get_(model_to_encoder[self.model_name])
        print(f"Using encoder, '{encoder}' for selected model, '{self.model_name}'")
        return encoder
    
    def get_token_length(self, text):
        if not isinstance(text, str):
            raise TypeError(f"Expected a string, but got {type(text).__name__}: {text}")
        return len(self.encoder.encode(text))
        
    def get_base_template_length(self):
        return sum([self.get_token_length(text) for text in [self.keywords, self.template]])
    
    def truncate_context(self, context, max_token_length, **kwargs):
        split_token = kwargs.get("split_token", "\n\n")

        df = pd.DataFrame({"paragraph": context.split(split_token)})
        df["paragraph_length"] = df.paragraph.apply(lambda x: self.get_token_length(x))
        df.sort_values("paragraph_length", ascending=False, inplace=True)
        df["cum_length"] = df["paragraph_length"].cumsum()
        df["keep"] = df.cum_length.apply(lambda x: x + self.base_length <= max_token_length)
        df = df[df.keep]
        df.sort_index(inplace=True)

        truncated = split_token.join(df.paragraph.tolist())
        return truncated
    
    def preprocess_documents(self, id: str="document_id", context: str="body", max_token_length: int=22_000, **kwargs):

        df = self.documents.copy()
        df["context_length"] = df[context].apply(lambda x: self.get_token_length(x))
        
        tasks = df.index
        truncated = 0
        for idx in tqdm(tasks, desc="Truncating overlength contexts"):
            if df.loc[idx, "context_length"] + self.base_length > max_token_length:
                df.at[idx, context] = self.truncate_context(df.loc[idx, context], max_token_length)
                df.at[idx, "context_length"] = self.get_token_length(df.loc[idx, context])
                truncated +=1
        print(f"Preprocessing complete. Truncated {truncated} documents.")
        self.preprocessed = df
    
    def load_prompt(self, context: str):
        return self.template.format(
            keywords=self.keywords,
            context=context
        )
    
    def generate_completion(self, context: str, **kwargs):
        prompt = self.load_prompt(context)
        system_prompt = kwargs.get("system_prompt", "You are a helpful assistant.")
        temperature = kwargs.get("temperature", 1.)
        max_tokens = kwargs.get( "max_tokens", 300)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content
    
    
    def is_rate_limited(self, response_text: str):
        """Basic heuristic for rate limit errors (can be replaced with specific error codes if using an API)."""
        return "rate limit" in response_text.lower() or "too many requests" in response_text.lower()


    def json_loads(self, text: str):
        """Attempt to load JSON safely."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}

    
    def extract_keywords(self, save_as: str, context="body", max_retries: int = 3, **kwargs):
        df = self.preprocessed.copy()
        
        if 'keywords' not in df.columns:
            df["keywords"] = None

        tasks = df[df["keywords"].isna()].index

        for task in tqdm(tasks, desc="Extracting keywords"):
            c = df.loc[task, context]

            retries = 0
            while retries <= max_retries:
                response = self.generate_completion(c)

                if self.is_rate_limited(response):
                    print(f"Rate limit hit on task {task}. Retrying in 30 seconds...")
                    time.sleep(60)
                    retries += 1
                    continue
                
                data = self.json_loads(response)
                extracted = data.get("keywords", [])

                if not isinstance(extracted, list):
                    print(f"Invalid or missing 'keywords' in response for task {task}. Skipping.")
                    break  # skip to next task

                # Write results to correct row
                df.at[task, "keywords"] = extracted

                break  # exit retry loop on success

            # Save after each task (optional: could be after batch instead)
            df.to_parquet(save_as)


        print("Keyword extraction completed.")
        self.documents = df