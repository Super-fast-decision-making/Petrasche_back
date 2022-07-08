from django.urls import path
from article import views

urlpatterns = [
    path('', views.ArticleView.as_view()),
    path('<int:pk>/', views.ArticleView.as_view()),
    path('comment/<int:pk>/', views.CommentView.as_view()),
]