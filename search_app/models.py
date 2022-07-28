import requests

es_url = 'http://localhost:9200'
# es_url = 'http://15.164.171.221:9200/'

article_analyzer_setting = {
  "settings": {
    "index": {
      "max_ngram_diff": 10,
      "analysis": {
        "filter": {
          "suggest_filter": {
            "type": "ngram",
            "min_gram": 2,
            "max_gram": 12
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
              "suggest_filter",
              "lowercase"
            ]
          }
        }
      }
    }
  }
}

res = requests.put(es_url+'/article/', json=article_analyzer_setting)


article_mapping_setting =  {
 "properties": {
    "content": {
      "type": "text",
      "store": "true",
      "analyzer": "suggest_index_analyzer",
      "search_analyzer": "suggest_search_analyzer"
    }
  }
}
res = requests.put(es_url+'/article/_mapping', json=article_mapping_setting)


hashtag_analyzer_setting = {
    "settings": {
            "index": {
                "analysis": {
                    "analyzer": {
                        "my_analyzer": {
                            "type": "custom",
                            "tokenizer": "nori_tokenizer",
                            "filter": [
                            "lowercase"
                            ]
                        }
                    }
                }
            }
        }
}
res = requests.put(es_url+'/hashtag/', json=hashtag_analyzer_setting)

