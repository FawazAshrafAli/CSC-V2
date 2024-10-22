from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import Http404, JsonResponse
from django.db.models import Q
import logging
import random

from services.models import Service
from .models import Blog, Category, Tag
from base.views import BaseView

logger = logging.getLogger(__name__)


class BaseBlogView(BaseView):
    model = Blog

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.all()
            context['ideal_blogs'] = Blog.objects.all()
            context['services'] = Service.objects.all()

            tag_list = list(Tag.objects.all())

            random_tags = random.sample(tag_list, 4)
            context['tags'] = random_tags
            
            return context
        except Exception:
            logger.exception("Error in fetching base context data of blog")
            return {}


class BlogListView(BaseBlogView, ListView):
    queryset = Blog.objects.all().order_by('-created_at')
    context_object_name = 'blogs'
    template_name = 'blog/list.html'


class BlogTagFilteredListView(BaseBlogView, ListView):
    context_object_name = 'blogs'
    template_name = 'blog/list.html'

    def get_queryset(self):
        try:
            self.tag = get_object_or_404(Tag, slug = self.kwargs['tag_slug'])
            return self.model.objects.filter(tags = self.tag).order_by('-created_at')
        except Http404:
            return None
        except Exception:
            logger.exception("Error in fetching tag filtered blogs")
            return []
        
    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['tag_name'] = self.tag
            return context
        except Exception:
            logger.exception("Error in fetching tag filtered context data of blog")
            return {}
    

class BlogDetailView(BaseBlogView, DetailView):    
    context_object_name = 'blog'
    template_name = 'blog/detail.html'


class SearchBlogView(BlogListView, ListView):

    def get_queryset(self):
        try:
            self.query = self.request.GET.get('q')
            if self.query:
                return Blog.objects.filter(
                    Q(title__icontains=self.query) | 
                    Q(content__icontains=self.query) | 
                    Q(summary__icontains=self.query) | 
                    Q(tags__name__icontains=self.query) | 
                    Q(category__name__icontains=self.query)
                    ).order_by('-created_at')
            
            return self.queryset.none()
        except Exception:
            logger.exception("Error in fetching search results")
            return self.queryset.none()

    def render_to_response(self, context):
        try:
            blogs = self.get_queryset()
            serialized_data = []
            for blog in blogs:
                serialized_data.append({
                    'id': blog.pk,
                    'title': blog.title,
                    'slug': blog.slug,
                    'summary': blog.summary,
                    'created_at': blog.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'image': blog.image.url if blog.image else None,
                    'tags': [tag.name for tag in blog.tags.all()],
                    'category': blog.category.name,
                })
            return JsonResponse({'data': serialized_data})
        except Exception:
            logger.exception("Error in rendering search results")
            return JsonResponse({'error': "Error in rendering search results"})
