import requests, json, os
from elasticsearch import Elasticsearch, exceptions


es_url = 'http://localhost:9200'
# es_url = 'http://15.164.171.221:9200/'

directory_path = 'path'
res = requests.get(es_url)
es = Elasticsearch(es_url)



try:
    es.indices.create(
        index='article',
        settings = {
            "index": {
            "analysis": {
                "filter": {
                "suggest_filter": {
                    "type": "edge_ngram",
                    "min_gram": 1,
                    "max_gram": 50
                }
                },
                "tokenizer": {
                "jaso_search_tokenizer": {
                    "type": "jaso_tokenizer",
                    "mistype": "true",
                    "chosung": "false"
                },
                "jaso_index_tokenizer": {
                    "type": "jaso_tokenizer",
                    "mistype": "true",
                    "chosung": "true"
                }
                },
                "analyzer": {
                "suggest_search_analyzer": {
                    "type": "custom",
                    "tokenizer": "jaso_search_tokenizer"
                },
                "suggest_index_analyzer": {
                    "type": "custom",
                    "tokenizer": "jaso_index_tokenizer",
                    "filter": [
                    "suggest_filter"
                    ]
                }
                }
            }
            }
        }        
)

except exceptions.RequestError as ex:
    print(80)
    if ex.error == 'resource_already_exists_exception':
        pass # Index already exists. Ignore.
    else: # Other exception - raise it
        raise ex

try:
    es.indices.create(
        index='hashtag',
        settings = {
            "index": {
                "analysis": {
                    "analyzer": {
                        "my_analyzer": {
                            "type": "custom",
                            "tokenizer": "nori_tokenizer"
                        }
                    }
                }
            }
        }
    )

except exceptions.RequestError as ex:
    print(28)
    if ex.error == 'resource_already_exists_exception':
        pass # Index already exists. Ignore.
    else: # Other exception - raise it
        raise ex

