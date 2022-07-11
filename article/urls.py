from django.urls import path
from article import views

urlpatterns = [
    path('', views.ArticleView.as_view()),
    path('<int:pk>/', views.ArticleView.as_view()),
    path('comment/<int:pk>/', views.CommentView.as_view()),
    path('like/<int:pk>/', views.LikeView.as_view()),
    path('myarticle/', views.MyArticleView.as_view()),
]