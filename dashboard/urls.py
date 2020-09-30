from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('project/<int:pk>/', views.project_detail, name='project-detail'),
    path('project/<int:pk>/story/create', views.StoryCreateView.as_view(), name='create-story'),
    path('story/<int:pk>/', views.StoryDetailView.as_view(), name='story-detail'),
    path('story/<int:pk>/update', views.StoryUpdateView.as_view(), name='update-story'),
    path('story/user/<int:pk>/update', views.UserStoryUpdateView.as_view(), name='update-user-story'),
]