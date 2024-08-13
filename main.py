import pysolr
from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Tuple
from transformers import AutoTokenizer, AutoModel
import numpy as np
from scipy.spatial.distance import cosine

# Initialize the Solr client
solr = pysolr.Solr('http://localhost:8983/solr/CORE-NAME', always_commit=True)

app = FastAPI()
# Initialize a language model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

# Initialize a cache dictionary for embeddings/
embedding_cache: Dict[str, List[float]] = {}

# Implement for get embedding.
def get_embedding(text):
    if text in embedding_cache:
        return embedding_cache[text]
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
    return embedding.flatten()

# Implement for compare the embedings.    
def compare_embeddings(query_embedding, doc_embedding):
    # Compute cosine similarity (1 - cosine distance)
    similarity = 1 - cosine(query_embedding, doc_embedding)
    return similarity

class QueryModel(BaseModel):
    question: str
    langcode: str

@app.post("/search")
def search(query: QueryModel):
    search = query.question
    langcode = query.langcode
    if not search:
        return ({"error": "No query provided"}), 400

    # Use Embedding to enhance the query
    enhanced_query = get_embedding(search)
    searchable_fields = [
        'ss_title^2.0',
        'sm_search_tag_string',
        'content',
        # Add other fields as needed
    ]
    qf_param = ' '.join(searchable_fields)
    
    try:
        results = solr.search(search, **{
            'defType': 'edismax',
            'qf': qf_param,
            'fq': ['ss_langcode:'+langcode],
            'rows': 5
        })
    except pysolr.SolrError as e:
        return ({"error": str(e)}), 500

    # Process Solr results
    enriched_results = []
    for result in results:
        data_doc = result.get('content')[0]
        doc_embedding = get_embedding(data_doc)
        similarity = compare_embeddings(enhanced_query, doc_embedding)
        enriched_results.append({
            'title': result.get('ss_title')[0],
            'content': result.get('content')[0],
            'similarity': similarity
        })
    sorted_results = sorted(enriched_results, key=lambda x: x["similarity"], reverse=True)
    return sorted_results
