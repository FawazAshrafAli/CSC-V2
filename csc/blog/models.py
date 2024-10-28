from django.db import models
from authentication.models import User
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Category.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'blog_category'

    def __str__(self):
        return self.name
    

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if self.name not in ['', ' '] and self.name is not None:
            if not self.slug:
                self.slug = slugify(self.name)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Blog(models.Model):
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = RichTextField()
    summary = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='blog_posts')

    def save(self, *args, **kwargs):        
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def get_tags(self):
        tags = self.tags.all()
        tag_count = self.tags.count()
        tag_string = ''
        for i in range(tag_count): 
            if i != tag_count - 1:
                tag_string += tags[i].name + ', '
            else:
                tag_string += tags[i].name
        return tag_string
    
    @property
    def get_categories(self):
        categories = self.categories.all()
        category_count = self.categories.count()
        category_string = ''
        for i in range(category_count):
            if i != category_count - 1:
                category_string += categories[i].name + ', '
            else:
                category_string += categories[i].name
        return category_string

    @property
    def previous_blog(self):
        blogs = Blog.objects.all().order_by('-created_at')
        current_blog_index = list(blogs).index(self)
        if current_blog_index > 0:
            return blogs[current_blog_index - 1]
        
        return None
    
    @property
    def next_blog(self):
        blogs = Blog.objects.all().order_by('-created_at')
        current_blog_index = list(blogs).index(self)
        if current_blog_index < len(blogs) - 1:
            return blogs[current_blog_index + 1]
        
        return None
    
    @property
    def list_tags(self):
        tag_string = ""
        if self.tags.exists():
            tag_list = [tag.name for tag in self.tags.all()]
            tag_string = ",".join(tag_list)
        return tag_string
    
    @property
    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})
    

    class Meta:
        ordering = ['-created_at']
        db_table = 'blog'

    def __str__(self):
        return self.title
