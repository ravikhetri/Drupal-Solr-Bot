import pysolr
from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Tuple

# Initialize the Solr client
solr = pysolr.Solr('http://localhost:8983/solr/CORE-NAME', always_commit=True)

app = FastAPI()

# Initialize a cache dictionary for embeddings/
embedding_cache: Dict[str, List[float]] = {}

class Embedding:
    def get_embedding(self, query):
        if query in embedding_cache:
            return embedding_cache[query]
        return query

class QueryModel(BaseModel):
    question: str
    langcode: str

@app.post("/search")
def search(query: QueryModel):
    
    search = query.question
    langcode = query.langcode
    langcode_str = langcode
    
    if not search:
        return ({"error": "No query provided"}), 400

    # Use Embedding to enhance the query
    emm_integration = Embedding()
    enhanced_query = emm_integration.get_embedding(search)
    searchable_fields = [
        'ss_title^2.0',
        'sm_search_tag_string',
        'content',
        # Add other fields as needed
    ]
    qf_param = ' '.join(searchable_fields)
    
    try:
        results = solr.search(enhanced_query, **{
            'defType': 'edismax',
            'qf': qf_param,
            'fq': ['ss_langcode:'+langcode],
            'rows': 5
        })
    except pysolr.SolrError as e:
        return ({"error": str(e)}), 500

    # Process Solr results
    response = []
    for result in results:
        response.append({
            'id': result.get('its_nid'),
            'title': result.get('title', ''),
            'content': result.get('content', ''),
        })

    return response
