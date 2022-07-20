import requests, json, os
from elasticsearch import Elasticsearch, exceptions


es_url = 'http://localhost:9200'
directory_path = 'path'
res = requests.get(es_url)
es = Elasticsearch(es_url)

try:
    es.indices.create(
        index='article',
            # 한글 형태소 분석기 nori를 통해 데이터를 토크나이징할 수 있도록 설정
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
        if ex.error == 'resource_already_exists_exception':
            pass # Index already exists. Ignore.
        else: # Other exception - raise it
            raise ex
