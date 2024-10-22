from django.urls import path
from .views import (
    BlogListView, BlogDetailView, BlogTagFilteredListView,
    SearchBlogView,
    )

app_name = "blog"

urlpatterns = [
    path('', BlogListView.as_view(), name="blogs"),
    path('tags/<str:tag_slug>', BlogTagFilteredListView.as_view(), name="tag_filtered_blogs"),
    path('detail/<str:slug>', BlogDetailView.as_view(), name="detail"),
    path('search/', SearchBlogView.as_view(), name="search")
]
