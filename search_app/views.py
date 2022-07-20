from django.shortcuts import render

from rest_framework.views import APIView  
from rest_framework.response import Response  
from rest_framework import status  
  
from elasticsearch import Elasticsearch  
import requests


class SearchView(APIView):

    def get(self, request):
        es_url = 'http://localhost:9200'
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

'''
        docs = es.search(
            index='dictionary',
            body={
                "query": {
                    "multi_match": {
                        "query": search_words,
                        "fields": [
                            "Restaurant", 
                            "Review"
                        ]
                    }
                }
            })

        data_list = []
        for data in docs['hits']['hits']:
            data_list.append(data.get('_source'))

        return Response(data_list)
'''   
    
'''
class ArticleSearchView(APIView):
    def get(self, request):
        words = request.query_params.get('words', '').strip()
        print("*****"+words)
        if words == '':
            return Response({'message': '검색어를 입력해 주세요.'}, status=status.HTTP_404_NOT_FOUND)
        words = words.split(' ')
        query = Q()
        for word in words:

            if word.strip() !="":
                query.add(Q(title__icontains=word.strip(), is_active=True, exposure_end_date__gte=today), Q.OR)
                query.add(Q(user__username__icontains=word.strip(), is_active=True, exposure_end_date__gte=today), Q.OR)

        articles = ArticleModel.objects.filter(query)

        if articles.exists():
            serializer = ArticleSerializer(articles, many=True)
            print("&&&&&&&&&&&&&")
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK) 

        return Response({'message': '검색된 게시물이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

'''