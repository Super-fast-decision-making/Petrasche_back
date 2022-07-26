from django.shortcuts import render

from rest_framework.views import APIView  
from rest_framework.response import Response  
from rest_framework import status  
  
from elasticsearch import Elasticsearch  
import requests


class SearchView(APIView):

    def get(self, request):
        es_url = 'http://localhost:9200'
        # es_url = 'http://15.164.171.221:9200/'
        
        es = Elasticsearch(es_url)

        # 검색어
        search_words = request.GET.get('search')
        # search_words = request.query_params.get('words', '').strip()
        
        if not search_words:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'search word param is missing'})

        es_url+'/article/_search?q='+ search_words 
        response = requests.get(es_url+'/article/_search?q='+ search_words)
        article_pk_list = []
        for obj in response['hits']['hits']:
            article_pk_list.append(obj["_source"]["pk"])
            
        
        return Response(response['hits']['hits'], status=status.HTTP_200_OK)

