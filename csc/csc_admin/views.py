from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView, CreateView, DetailView, UpdateView, ListView
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import authenticate, logout
from django.db.models import Count, Q
import logging
import re

from .forms import (
    CreateServiceForm, UpdateServiceForm, CreateBlogForm,
    UpdateBlogForm
    )

from contact_us.models import Enquiry
from faq.models import Faq
from authentication.models import User
from products.models import Product, Category as ProductCategory, ProductEnquiry as UserProductEnquiry
from csc_center.models import CscCenter, State, District, Block, CscKeyword, CscNameType, SocialMediaLink, Banner
from services.models import Service, ServiceEnquiry as UserServiceEnquiry
from blog.models import Blog, Category as BlogCategory, Tag
from posters.models import Poster
from .models import CscCenterAction, ServiceEnquiry as AdminServiceEnquiry, ProductEnquiry as AdminProductEnquiry
from payment.models import Payment, Price

from .tasks import send_confirm_creation, send_offer_mail

logger = logging.getLogger(__name__)

@method_decorator(never_cache, name="dispatch")
class BaseAdminView(LoginRequiredMixin, View):
    login_url = reverse_lazy("authentication:login")
    redirect_url = login_url

    def dispatch(self, request, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                return redirect(self.login_url)
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.exception("Error in base admin view: %s", e)
            return redirect(self.redirect_url)

        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['services'] = Service.objects.all()
        except Exception as e:
            logger.exception("Error in fetching context data of base admin view: %s", e)

        return context    


class AdminHomeView(BaseAdminView, TemplateView):
    template_name = 'admin_home/home.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        try:
            context['csc_centers'] = CscCenter.objects.all()
            context['services'] = Service.objects.all()
            context['products'] = Product.objects.all()
            context['posters'] = Poster.objects.all()
            context['home_page'] = True
            return context
        except Exception as e:
            logger.exception("Error in fetching context data of admin home view: %s", e)
        return context

##################################### SERVICE START #####################################
class AdminBaseServiceView(BaseAdminView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['service_page'] = True
        except Exception as e:
            logger.exception("Error in fetching context data of admin base service view: %s", e)

        return context


class CreateServiceView(AdminBaseServiceView, CreateView):
    model = Service
    form_class = CreateServiceForm
    template_name = 'admin_service/create.html'
    success_url = reverse_lazy('csc_admin:create_service')
    redirect_url = success_url
    
    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()
            name = request.POST.get('name').strip()
            image = request.FILES.get('image')

            if name:
                self.service = self.model.objects.create(name = name, image = image)
                if form.is_valid():
                    description = form.cleaned_data['description']
                    self.service.description = description
                    self.service.save()

                messages.success(request, 'Successfully created new service.')
                return redirect(self.success_url)
            else:
                messages.warning(request, 'Please provide the service name.')
                return redirect(self.redirect_url)
        except Exception as e:
            logger.exception("Error in creating new service: %s", e)
            messages.error(request, 'Failed to create new service.')
            return redirect(self.redirect_url)
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            service = self.model.objects.all().last()
            context['service'] = service
            context['form'] = self.get_form()
        except Exception as e:
            logger.exception("Error in fetching context data of create service view: %s", e)

        return context
                                    

class UpdateServiceView(AdminBaseServiceView, UpdateView):
    model = Service
    form_class = UpdateServiceForm
    template_name = 'admin_service/update.html'
    context_object_name = "service"

    def get_success_url(self, **kwargs):
        try:
            return reverse_lazy('csc_admin:service', kwargs = {'slug' : self.kwargs['slug']})
        except Exception as e:
            logger.exception("Error in getting success url of update service view: %s", e)
            return ''
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception("Error in getting redirect url of update service view: %s", e)
            return ''
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            form = self.get_form()

            name = request.POST.get('name').strip()
            image = request.FILES.get('image')

            if name:
                if form.is_valid():
                    form.save(commit=False)
                    self.object.name = name                
                    self.object.image = image if image else self.object.image
                    self.object.save()

                    messages.success(request, "Service details successfully updated.")        
                    return redirect(self.get_success_url())
                else:
                    messages.error(request, "Error in updation details of service.")
                    return self.form_invalid(form)
            else:
                messages.error(request, "Please Provide a service name")
                return self.form_invalid(form)
        except Exception as e:
            logger.exception("Error in updating service view: %s", e)
            messages.error(request, "Error in service updation.")
            return redirect(self.get_redirect_url())

    def form_invalid(self, form):
        try:
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Erron on field - {field}: {error}")
            return redirect(self.get_redirect_url())
        except Exception as e:
            logger.exception("Error in updating service view: %s", e)
            return redirect(self.get_redirect_url())


class ListServiceView(AdminBaseServiceView, ListView):
    model = Service
    queryset = Service.objects.all()
    template_name = 'admin_service/list.html'
    context_object_name = "services"
    

class DetailServiceView(AdminBaseServiceView, DetailView):
    model = Service
    template_name = 'admin_service/detail.html'
    context_object_name = "service"
    form_class = UpdateServiceForm
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['form'] = self.form_class(instance=self.object)
        except Exception as e:
            logger.exception("Error in getting context data for detail service view: %s", e)

        return context
    

class DeleteServiceView(AdminBaseServiceView, View):
    model = Service
    success_url = reverse_lazy('csc_admin:services')
    redirect_url = success_url

    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(Service, slug = self.kwargs['slug'])
            self.object.delete()
            messages.success(self.request, "Successfully deleted service.")
            return redirect(self.success_url)
        
        except Http404:            
            messages.error(self.request, "Invalid service")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception("Error in deleting service view: %s", e)
            return redirect(self.redirect_url)



class ServiceEnquiryListView(AdminBaseServiceView, ListView):
    model = AdminServiceEnquiry
    queryset = model.objects.all().order_by('-created')
    context_object_name = "enquiries"
    template_name = "admin_service/enquiry_list.html"


class DeleteServiceEnquiryView(AdminBaseServiceView, View):
    model = AdminServiceEnquiry
    success_url = redirect_url = reverse_lazy("csc_admin:service_enquiries")

    def get_object(self):
        try:
            return get_object_or_404(AdminServiceEnquiry, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Service Enquiry")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception("Error in getting service enquiry object for deletion: %s", e)
            return redirect(self.redirect_url)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()        
            self.object.delete()
            messages.success(self.request, "Successfully deleted service enquiry.")
            return redirect(self.success_url)
        except Exception as e:
            logger.exception("Error in deleting service enquiry.: %s", e)
            return redirect(self.redirect_url)


# Nuclear Views
class RemoveServiceImageView(AdminBaseServiceView, UpdateView):
    model = Service
    field = ['image']    
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.image = None
            self.object.save()
            return JsonResponse({"message": "Successfully removed image."})
        except Exception as e:
            logger.exception("Error in removing service image.: %s", e)
            return JsonResponse({"error": "Error in removing service image"})

##################################### SERVICE END #####################################


##################################### BLOG START #####################################

class BaseAdminBlogView(BaseAdminView, View):
    model = Blog

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['blog_page'] = True
        except Exception as e:
            logger.exception("Error in getting context data for admin blog view.: %s", e)

        return context

class BlogListView(BaseAdminBlogView, ListView):
    template_name = 'admin_blog/list.html'
    queryset = Blog.objects.all()
    context_object_name = 'blogs'


class BlogDetailView(BaseAdminBlogView, DetailView):
    template_name = 'admin_blog/detail.html'
    query_pk_and_slug = 'slug'


class CreateBlogView(BaseAdminBlogView, CreateView):
    template_name = 'admin_blog/create.html'
    success_url = reverse_lazy('csc_admin:create_blog')
    redirect_url = success_url
    form_class = CreateBlogForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['form'] = self.get_form()
            context['categories'] = BlogCategory.objects.all().order_by('name')
        except Exception as e:
            logger.exception("Error in getting context data for create blog view.: %s", e)

        return context

    def post(self, request, *args, **kwargs):
        try:
            title = request.POST.get('title').strip()
            image = request.FILES.get('image')        
            category = request.POST.get('category')
            summary = request.POST.get('summary').strip()
            author = request.user
            tags = request.POST.get('tags').strip()

            category = get_object_or_404(BlogCategory, slug = category)

            if Blog.objects.filter(title = title).exists():
                messages.error(request, 'Blog with this title already exists. Please try again with another title')            
                return redirect(self.redirect_url)
        
            form = self.get_form()
            if form.is_valid():
                content = form.cleaned_data['content']
                blog = Blog.objects.create(
                    title = title, image = image, author = author,
                    summary = summary, content = content, category = category
                    )
                
                if tags:
                    tag_list = tags.split(',')
                    for tag in tag_list:
                        tag = tag.strip().title()
                        if tag not in (' ', ','):
                            tag_obj = Tag.objects.filter(name = tag)                                                        
                            if not tag_obj.exists():
                                tag_obj = Tag.objects.create(name = tag)
                            else:
                                tag_obj = tag_obj.first().pk
                            blog.tags.add(tag_obj)
                            blog.save()                                    

                messages.success(request, "Blog Saved")
                return redirect(self.success_url)
            else:
                messages.error(request, "Content cannot be empty.")
            
        except Http404:
            messages.error(request, "Invalid blog category. Please select a valid blog category and try again.")

        except Exception as e:
            logger.exception("Error in creating blog.: %s", e)

        return redirect(self.redirect_url)


class UpdateBlogView(BaseAdminBlogView, UpdateView):
    template_name = 'admin_blog/update.html'
    form_class = UpdateBlogForm
    pk_url_kwarg = 'slug'

    def get_success_url(self):
        try:
            return reverse_lazy('csc_admin:blog', kwargs={'slug': self.object.slug})
        except Exception as e:
            logger.exception("Error in getting success url for blog update view: %s", e)
            return ''
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception("Error in getting redirect url for blog update view: %s", e)
            return ''

    def get_object(self, **kwargs):
        try:
            return get_object_or_404(Blog, slug = self.kwargs[self.pk_url_kwarg])
        except Http404:
            messages.error(self.request, "Invalid Blog")
            return redirect(self.get_redirect_url())
        except Exception as e:
            logger.exception("Error in getting blog object for update view: %s", e)
            return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['form'] = self.get_form()
            context['categories'] = BlogCategory.objects.all().order_by('name')
        except Exception as e:
            logger.exception("Error in getting context data for blog update view: %s", e)

        return context

    def post(self, request, *args, **kwargs):
        try:
            title = request.POST.get('title').strip()
            image = request.FILES.get('image')        
            category_list = request.POST.getlist('category')
            summary = request.POST.get('summary').strip()
            author = request.user
            tags = request.POST.get('tags').strip()
        
            form = self.get_form()
            if form.is_valid():
                content = form.cleaned_data['content']
                self.object = self.get_object()
                self.object.title = title
                self.object.summary = summary
                self.object.author = author
                self.object.content = content
                if image:
                    self.object.image = image
                self.object.save()

                if category_list:
                    self.object.categories.set(category_list)
                    self.object.save()
                
                if tags:
                    tag_list = tags.split(',')
                    for tag in tag_list:
                        tag = tag.strip().title()
                        if tag not in (' ', ',', ''):
                            tag_obj = Tag.objects.filter(name = tag)                                                        
                            if not tag_obj.exists():
                                tag_obj = Tag.objects.create(name = tag)
                            else:
                                tag_obj = tag_obj.first().pk                                
                            self.object.tags.add(tag_obj)
                            self.object.save()                                    

                messages.success(request, "Blog Saved")
                return redirect(self.get_success_url())
            else:
                messages.error(request, "Content field cannot be empty.")
                self.redirect_url = self.success_url
                return redirect(self.get_redirect_url())
        except Exception as e:
            logger.exception("Error in blog update view: %s", e)
            return redirect(self.get_redirect_url())


class DeleteBlogView(BaseAdminBlogView, View):
    success_url = redirect_url = reverse_lazy('csc_admin:blogs')

    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(Blog, slug = self.kwargs['slug'])
            self.object.delete()
            messages.success(self.request, "Successfully deleted blog.")
            return redirect(self.success_url)
        except Http404:            
            messages.error(request, "Invalid Blog")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception("Error in blog delete view: %s", e)
            return redirect(self.redirect_url)


# Nuclear
class RemoveBlogImageView(BaseAdminBlogView, UpdateView):
    field = ['image']    
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.image = None
            self.object.save()
            return JsonResponse({"message": "Successfully removed image."})
        except Exception as e:
            logger.exception("Error in blog image delete view: %s", e)
            return JsonResponse({"error": "Error in removing blog image"})
        

class AddBlogCategoryView(CreateBlogView):
    model = BlogCategory
    fields = ['name']

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")

            if not name:
                messages.warning(request, "Please provide the blog category and try again")            
            else:
                if not self.model.objects.filter(name = name).exists():        
                    self.model.objects.create(name = name)
                    messages.success(self.request, "Blog category creation succesfull")
                    return redirect(self.success_url)                
                else:
                    messages.error(request, "The entered blog category already exists")

            return redirect(self.redirect_url)
                
        except Exception as e:
            messages.error(self.request, "Blog category creation failed")
            logger.exception(f"Error in blog category creation view: {e}")
            return redirect(self.redirect_url)
        
class BlogCategoryListView(BaseAdminBlogView, ListView):
    model = BlogCategory
    queryset = model.objects.all()
    context_object_name = "categories"
    template_name = "admin_blog/list_categories.html"


class UpdateBlogCategoryView(BaseAdminBlogView, UpdateView):
    model = BlogCategory
    fields = ['name']
    template_name = "admin_blog/update_category.html"
    success_url = redirect_url = reverse_lazy("csc_admin:blog_categories")
    context_object_name = "category"

    def get_success_url(self):
        try:
            return reverse_lazy("csc_admin:update_blog_category", kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get success url of blog category update view: {e}")
            return redirect(self.success_url)
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in get redirect url of blog category update view: {e}")
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")

            if not name:
                messages.warning(request, "Please provide the blog category and try again")            
            else:
                if not self.model.objects.filter(name = name).exists():
                    self.object = self.get_object()
                    self.object.name = name
                    self.object.save()                    
                    messages.success(self.request, "Blog category updation succesfull")
                    return redirect(self.get_success_url())                
                else:
                    messages.error(request, "The entered blog category already exists")

            return redirect(self.get_redirect_url())
                
        except Exception as e:
            messages.error(self.request, "Blog category updation failed")
            logger.exception(f"Error in blog category updation view: {e}")
            return redirect(self.redirect_url)

class DeleteBlogCategoryView(BaseAdminBlogView, View):
    model = BlogCategory
    success_url = redirect_url = reverse_lazy("csc_admin:blog_categories")

    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get('slug'))
            self.object.delete()
            messages.success(self.request, "Blog category deletion successful")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Invalid blog category.")

        except Exception as e:
            logger.exception(f"Error in blog category deletion view: {e}")
            messages.error(request, "Blog deletion failed!")

        return redirect(self.redirect_url)
    
##################################### BLOG END #####################################

##################################### PRODUCT START #####################################

class BaseAdminCscProductView(BaseAdminView, View):
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['product_categories'] = ProductCategory.objects.all().order_by('name')
            context['product_page'] = True       
        except Exception as e:
            logger.exception("Error in fetchin admin base product context data: %s", e)

        return context
    

class CreateProductView(BaseAdminCscProductView, CreateView):
    fields = ["image", "name", "description", "price", "category"]
    template_name = "admin_product/create.html"
    success_url= redirect_url = reverse_lazy("csc_admin:create_product")

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get('name').strip()
            image = request.FILES.get('image')
            description = request.POST.get('description').strip()
            price = request.POST.get('price').strip()
            category = request.POST.get('category').strip()

            try:
                category = get_object_or_404(ProductCategory, slug = category)
            except Http404:
                messages.error(self.request, "Failed. Invalid category")
                return redirect(self.redirect_url)
            
            self.model.objects.create(name = name, image = image, description = description, price = price, category = category)
            messages.success(self.request, "Created Product")
            return redirect(self.success_url)
        except Exception as e:
            logger.exception("Error in creating product: %s", e)
            messages.error(request, "Error in creating product")
            return redirect(self.redirect_url)
    
    def form_invalid(self, form):
        try:
            response = super().form_invalid(form)
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error on field '{field}': {error}")                
            return response
        except Exception as e:
            logger.exception("Error in creating product: %s", e)
            messages.error(self.request, "Error in creating product")
            return redirect(self.redirect_url)
    

class ProductListView(BaseAdminCscProductView, ListView):
    template_name = "admin_product/list.html"
    context_object_name = "products"


class ProductDetailView(BaseAdminCscProductView, DetailView):
    template_name = "admin_product/detail.html"
    context_object_name = "product"


class UpdateProductView(BaseAdminCscProductView, UpdateView):
    fields = ["image", "name", "description", "price", "category"]
    template_name = "admin_product/update.html"
    
    def get_success_url(self, *kwargs):
        try:
            return reverse_lazy("csc_admin:product", kwargs = {"slug" : self.object.slug})
        except Exception as e:
            logger.exception("Error in getting success url of admin product update view: %s", e)
            return ''
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception("Error in getting redirect url of admin product update view: %s", e)
            return ''
    
    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get('name').strip()
            image = request.FILES.get('image')
            description = request.POST.get('description').strip()
            price = request.POST.get('price').strip()
            category = request.POST.get('category').strip()

            try:
                category = get_object_or_404(ProductCategory, slug = category)
            except Http404:
                messages.error(self.request, "Failed. Invalid category")
                return redirect(self.get_redirect_url())
            
            self.object = self.get_object()
            if not image:
                image = self.object.image
            
            self.object.name = name
            self.object.image = image
            self.object.description = description
            self.object.price = price
            self.object.category = category
            self.object.save()

            messages.success(self.request, "Updated Product")
            return redirect(self.get_success_url())
        except Exception as e:
            logger.exception("Error in admin product update view: %s", e)
            messages.error("Error in updating product")
            return redirect(self.get_redirect_url())

    def form_invalid(self, form):
        try:     
            response = super().form_invalid(form)        

            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error on field '{field}': {error}")
            return response
        except Exception as e:
            logger.exception("Error in admin product update view: %s", e)
            return redirect(self.get_success_url())
    

class DeleteProductView(BaseAdminCscProductView, View):
    success_url = redirect_url = reverse_lazy('csc_admin:products')

    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = kwargs['slug'])            
            self.object.delete()
            messages.success(self.request, "Deleted Product")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, 'Invalid Product')
            return redirect(reverse_lazy('csc_admin:products'))    
    
        except Exception as e:
            logger.exception("Error in admin product delete view: %s", e)
            messages.error(self.request, "Error in deleting product")
            return redirect(self.redirect_url)


def get_product_categories(request):
    try:
        categories = list(ProductCategory.objects.all().values('slug', 'name'))
        return JsonResponse({"categories": categories})
    except Exception as e:
        msg = "Error in getting product categories"
        logger.exception(f"{msg}: %s", e)
        return JsonResponse({"error": msg})


class BaseProductCategoryView(BaseAdminCscProductView, View):
    model = ProductCategory

class ProductCategoryListView(BaseProductCategoryView, ListView):
    queryset = ProductCategory.objects.all()
    context_object_name = "categories"
    template_name = "admin_product/list_categories.html"
    


class AddProductCategoryView(BaseProductCategoryView, CreateView):
    fields = ["name"]
    template_name = "admin_product/add_category.html"
    success_url = redirect_url = reverse_lazy("csc_admin:add_product_category")

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")

            if not name:
                messages.warning(request, "Please provide the product category and try again")            
            else:
                if not self.model.objects.filter(name = name).exists():        
                    self.model.objects.create(name = name)
                    messages.success(self.request, "Product category creation succesfull")
                    return redirect(self.success_url)                
                else:
                    messages.error(request, "The entered product category already exists")

            return redirect(self.redirect_url)
                
        except Exception as e:
            messages.error(self.request, "Product category creation failed")
            logger.exception(f"Error in product category creation view: {e}")
            return redirect(self.redirect_url)


class UpdateProductCategoryView(BaseProductCategoryView, UpdateView):
    fields = ['name']
    template_name = "admin_product/update_category.html"
    success_url = redirect_url = reverse_lazy("csc_admin:product_categories")
    context_object_name = "category"

    def get_success_url(self):
        try:
            return reverse_lazy("csc_admin:update_product_category", kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get success url of product category update view: {e}")
            return redirect(self.success_url)
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in get redirect url of product category update view: {e}")
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")

            if not name:
                messages.warning(request, "Please provide the product category and try again")            
            else:
                if not self.model.objects.filter(name = name).exists():
                    self.object = self.get_object()
                    self.object.name = name
                    self.object.save()                    
                    messages.success(self.request, "Product category updation succesfull")
                    return redirect(self.get_success_url())                
                else:
                    messages.error(request, "The entered product category already exists")

            return redirect(self.get_redirect_url())
                
        except Exception as e:
            messages.error(self.request, "Product category updation failed")
            logger.exception(f"Error in product category updation view: {e}")
            return redirect(self.redirect_url)
    

class DeleteProductCategoryView(BaseProductCategoryView, View):
    success_url = redirect_url = reverse_lazy("csc_admin:product_categories")

    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get('slug'))
            self.object.delete()
            messages.success(request, "Product category deletion successful")
            return redirect(self.success_url)
        except Http404:
            messages.error(request, "invalid product category")
        except Exception as e:
            messages.error(request, "Failed to delete product category")
            logger.exception(f"Error in deleting product category: {e}")
        
        return redirect(self.redirect_url)


class ProductEnquiryListView(BaseAdminCscProductView, ListView):
    model = AdminProductEnquiry
    queryset = model.objects.all().order_by('-created')
    context_object_name = "enquiries"
    template_name = "admin_product/enquiry_list.html"


class DeleteProductEnquiryView(BaseAdminCscProductView, View):
    model = AdminProductEnquiry
    success_url = redirect_url = reverse_lazy("csc_admin:product_enquiries")

    def get_object(self):
        try:
            return get_object_or_404(AdminProductEnquiry, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Product Enquiry")
            return redirect(self.redirect_url)
        except Exception as e:
            msg = "Error in getting product enquiry"
            logger.exception(f"{msg}: %s", e)
            messages.error(self.request, msg)
            return redirect(self.redirect_url)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()        
            self.object.delete()
            messages.success(self.request, "Successfully deleted product enquiry.")
            return redirect(self.success_url)
        except Exception as e:
            msg = "Error in deleting product enquiry"
            logger.exception(f"{msg}: %s", e)
            messages.error(self.request, msg)
            return redirect(self.redirect_url)
        
##################################### PRODUCT END #####################################

##################################### CSC CENTER START #####################################

class BaseAdminCscCenterView(BaseAdminView):
    model = CscCenter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['csc_center_page'] = True
            context.update({
                'states': State.objects.all().order_by('state'),
                'districts': District.objects.all().order_by('district'),
                'blocks': Block.objects.all().order_by('block'),
                })
        except Exception as e:
            logger.exception("Error in fetchin admin csc center context data: %s", e)

        return context


class ListCscCenterRequestView(BaseAdminCscCenterView, ListView):
    queryset = CscCenter.objects.filter(is_active = False, status = "Not Viewed").order_by("-created")
    template_name = 'admin_csc_center/request_list.html'
    context_object_name = "csc_centers"
    paginate_by = 10
    ordering = ['-created']


class CscCenterRequestDetailView(BaseAdminCscCenterView, DetailView):
    context_object_name = 'csc_center'
    template_name = 'admin_csc_center/request_detail.html'
    slug_url_kwarg = 'slug'


class RejectCscCenterRequestView(BaseAdminCscCenterView, UpdateView):
    success_url = reverse_lazy('csc_admin:csc_center_requests')
    redirect_url = success_url
    fields = ['status']

    def get_redirect_url(self):
        try:
            self.object = self.get_object()
            return reverse_lazy('csc_admin:csc_center_request', kwargs={'slug': self.object.slug}) if self.object else None  
        except Exception as e:
            logger.exception("Error in fetching redirect url of csc center rejection: %s", e)
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        rejection_reason = request.POST.get('rejection_reason')
        rejection_reason = rejection_reason.strip() if rejection_reason else None
        self.object = self.get_object()

        if rejection_reason:
            CscCenterAction.objects.create(csc_center = self.object, rejection_reason = rejection_reason)
            self.object.status = "Rejected"
            self.object.save()
            messages.success(request, "Request Rejected")
            return redirect(self.get_success_url())
        else:
            messages.error(request, "Request rejection failed.")
            return redirect(self.get_redirect_url())


class ListRejectedCscCenterRequestView(BaseAdminCscCenterView, ListView):
    model = CscCenterAction
    queryset = model.objects.exclude(rejection_reason = "").order_by("-created")
    template_name = 'admin_csc_center/rejected_list.html'
    context_object_name = "actions"
    ordering = ['-created']
    paginate_by = 10   


class RejectedCscCenterRequestDetailView(BaseAdminCscCenterView, DetailView):
    model = CscCenterAction
    context_object_name = 'csc_center'
    template_name = 'admin_csc_center/rejected_detail.html'
    slug_url_kwarg = 'slug'


class CancelCscCenterRejectionView(BaseAdminCscCenterView, UpdateView):
    fields = ['status']
    success_url = reverse_lazy('csc_admin:rejected_csc_centers')
    redirect_url = success_url

    def get_redirect_url(self):
        try:
            return reverse_lazy('csc_admin:rejected_csc_center', kwargs = {'slug' : self.kwargs.get('slug')})
        except Exception as e:
            logger.exception("Error in fetching redirect url of csc center rejection cancel view: %s", e)
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.status = "Not Viewed"
            self.object.save()
            try:
                csc_center_action = get_object_or_404(CscCenterAction, csc_center__slug = self.kwargs.get('slug'))
                csc_center_action.delete()
            except Http404:
                pass
            messages.success(request, "Cancelled csc center request rejection")
            return redirect(self.get_success_url())
        except Exception as e:
            logger.exception("Error in cancelling rejection: %s", e)
            messages.error(request, "Cancelling csc center request rejection failed")
            return redirect(self.get_redirect_url())


class ReturnCscCenterRequestView(BaseAdminCscCenterView, UpdateView):
    success_url = reverse_lazy('csc_admin:csc_center_requests')
    redirect_url = success_url
    fields = ['status']

    def get_redirect_url(self):
        try:
            self.object = self.get_object()
            return reverse_lazy('csc_admin:csc_center_request', kwargs={'slug': self.object.slug}) if self.object else None
        except Exception as e:
            logger.exception("Error in fetchin the redirect url of csc center return view: %s", e)
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            feedback = request.POST.get('feedback')
            feedback = feedback.strip() if feedback else None
            self.object = self.get_object()

            if feedback:                
                CscCenterAction.objects.create(csc_center = self.object, feedback = feedback)
                self.object.status = "Returned"
                self.object.save()
                messages.success(request, "Request Returned")
                return redirect(self.get_success_url())
            else:
                messages.error(request, "Request returning failed.")
                return redirect(self.get_redirect_url())
        except Exception as e:
            logger.exception("Error in returning csc center request: %s", e)
            messages.error(request, "Request returning failed.")
            return redirect(self.get_redirect_url())


class ListReturnedCscCenterRequestView(BaseAdminCscCenterView, ListView):
    model = CscCenterAction
    queryset = model.objects.exclude(feedback = "").order_by('-created')
    template_name = 'admin_csc_center/returned_list.html'
    context_object_name = "csc_centers"
    ordering = ['-created']
    paginate_by = 10


class ReturnedCscCenterRequestDetailView(BaseAdminCscCenterView, DetailView):
    model = CscCenterAction
    context_object_name = 'csc_center'
    template_name = 'admin_csc_center/returned_detail.html'
    slug_url_kwarg = 'slug'


class CancelCscCenterReturnView(BaseAdminCscCenterView, UpdateView):
    fields = ['status']
    success_url = reverse_lazy('csc_admin:returned_csc_centers')
    redirect_url = success_url

    def get_redirect_url(self):
        try:
            return reverse_lazy('csc_admin:returned_csc_center', kwargs = {'slug' : self.kwargs.get('slug')})
        except Exception as e:
            logger.exception("Error in fetchin the redirect url of csc center return cancel view: %s", e)
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.status = "Not Viewed"
            self.object.save()
            try:
                csc_center_action = get_object_or_404(CscCenterAction, csc_center__slug = self.kwargs.get('slug'))
                csc_center_action.delete()
            except Http404:                
                pass
            messages.success(request, "Cancelled csc center request return")
            return redirect(self.get_success_url())
        
        except Exception as e:
            msg = "Cancelling csc center request return failed"
            logger.exception(f"{msg}: %s", e)
            messages.error(request, msg)
            return redirect(self.get_redirect_url())


class ApproveCscCenterRequestView(BaseAdminCscCenterView, UpdateView):
    success_url = redirect_url = reverse_lazy('csc_admin:csc_center_requests')
    fields = ['status']


    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            payment_link = f"https://{request.get_host()}/payment/{self.object.slug}"
            
            if self.object.email and payment_link:
                center_data = {
                    "email": self.object.email,
                    "name": self.object.name,
                    "owner": self.object.owner if self.object.owner else self.object.email
                }
                send_confirm_creation.delay(center = center_data, payment_link = payment_link)

                self.object.status = "Approved"
                self.object.save()

            messages.success(request, "Request Approved")
            return redirect(self.get_success_url())
        except Exception as e:
            msg = "Approving csc center request failed"
            logger.exception(f"{msg}: %s", e)
            messages.error(request, msg)
            return redirect(self.redirect_url)
    

class ListApprovedCscCenterRequestView(BaseAdminCscCenterView, ListView):    
    queryset = CscCenter.objects.filter(status = "Approved").order_by('-created')
    template_name = 'admin_csc_center/approved_list.html'
    context_object_name = "csc_centers"


class ApprovedCscCenterRequestDetailView(BaseAdminCscCenterView, DetailView):    
    context_object_name = 'csc_center'
    template_name = 'admin_csc_center/approved_detail.html'
    slug_url_kwarg = 'slug'


class CancelCscCenterApprovalView(BaseAdminCscCenterView, UpdateView):
    fields = ['status']
    success_url = reverse_lazy('csc_admin:approved_csc_centers')
    redirect_url = success_url

    def get_redirect_url(self):
        try:
            return reverse_lazy('csc_admin:approved_csc_center', kwargs = {'slug' : self.kwargs.get('slug')})
        except Exception as e:
            logger.exception("Error in fetchin the redirect url of csc center cancel view.: %s", e)
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.status = "Not Viewed"
            self.object.save()        
            messages.success(request, "Cancelled csc center request approval")
            return redirect(self.get_success_url())
        except Exception as e:
            msg = "Cancelling csc center request approval Failed"
            logger.exception(f"{msg}: %s", e)
            messages.error(request, msg)
            return redirect(self.get_redirect_url())


class ListCscCenterView(BaseAdminCscCenterView, ListView):
    template_name = "admin_csc_center/list.html"
    ordering = ['name']
    context_object_name = 'centers'
    queryset = CscCenter.objects.all().order_by('name')
    paginate_by = 10   

    def get_queryset(self):
        try:
            state = self.kwargs.get('state')
            district = self.kwargs.get('district')
            block = self.kwargs.get('block')
            
            queryset = self.queryset

            if state:
                queryset = queryset.filter(state__pk=state)
            if district:
                queryset = queryset.filter(district__pk=district)
            if block:
                queryset = queryset.filter(block__pk=block)
                
            return queryset
        except Exception as e:
            logger.exception("Error in fetching csc center queryset in list csc center view.: %s", e)
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            
            state = self.kwargs.get('state')
            district = self.kwargs.get('district')
            block = self.kwargs.get('block')

            context['state'] = state if state else None

            context['districts'] = District.objects.filter(state__pk = state).order_by("district") if state else None
            context['district'] = district if district else None

            context['blocks'] = Block.objects.filter(state__id = state, district_id = district).order_by("block") if state and district else None
            context['block_id'] = block if block else None

        except Exception as e:
            logger.exception("Error in fetching context data in list csc center view.: %s", e)

        return context


class AddCscCenterView(BaseAdminCscCenterView, CreateView):
    template_name = 'admin_csc_center/create.html'
    success_url = redirect_url = reverse_lazy('csc_admin:add_csc')
    fields = "__all__"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['name_types'] = CscNameType.objects.all().order_by('type')
            context['keywords'] = CscKeyword.objects.all().order_by('keyword')
            context['products'] = Product.objects.all()
            context['states'] = State.objects.all()
            context['social_medias'] = ["Facebook", "Instagram", "Twitter", "YouTube", "LinkedIn", "Pinterest", "Tumblr"]

            time_data = []
            for i in range(1, 25):
                if i < 13:
                    str_time = f"{i} AM"
                else:
                    str_time = f"{i-12} PM"            
                time = datetime.strptime(str_time, "%I %p").strftime("%H:%M")
                time_data.append({"str_time": str_time, "time": time})
                context['time_data'] = time_data

        except Exception as e:
            logger.exception("Error in fetching context data in add csc center view.: %s", e)

        return context

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get('name')
            type = request.POST.get('type')
            csc_reg_no = request.POST.get('csc_reg_no')
            keywords = request.POST.getlist('keywords')

            state = request.POST.get('state')
            district = request.POST.get('district')
            block = request.POST.get('block')
            location = request.POST.get('location')
            zipcode = request.POST.get('zipcode')
            landmark_or_building_name = request.POST.get('landmark_or_building_name')
            street = request.POST.get('address')
            logo = request.FILES.get('logo')
            banners = request.FILES.getlist('banner')
            description = request.POST.get('description')
            owner = request.POST.get('owner')
            email = request.POST.get('email')
            website = request.POST.get('website')
            contact_number = request.POST.get('contact_number')
            mobile_number = request.POST.get('mobile_number')
            whatsapp_number = request.POST.get('whatsapp_number')
            services = request.POST.getlist('services')
            products = request.POST.getlist('products')

            show_opening_hours = request.POST.get('show_opening_hours')
            if show_opening_hours: 
                show_opening_hours = show_opening_hours.strip()

            if show_opening_hours:
                mon_opening_time = request.POST.get('mon_opening_time')
                tue_opening_time = request.POST.get('tue_opening_time')
                wed_opening_time = request.POST.get('wed_opening_time')
                thu_opening_time = request.POST.get('thu_opening_time')
                fri_opening_time = request.POST.get('fri_opening_time')
                sat_opening_time = request.POST.get('sat_opening_time')
                sun_opening_time = request.POST.get('sun_opening_time')

                mon_closing_time = request.POST.get('mon_closing_time')
                tue_closing_time = request.POST.get('tue_closing_time')
                wed_closing_time = request.POST.get('wed_closing_time')
                thu_closing_time = request.POST.get('thu_closing_time')
                fri_closing_time = request.POST.get('fri_closing_time')
                sat_closing_time = request.POST.get('sat_closing_time')
                sun_closing_time = request.POST.get('sun_closing_time')

                mon_opening_time = mon_opening_time if mon_opening_time.strip() else None
                tue_opening_time = tue_opening_time if tue_opening_time.strip() else None
                wed_opening_time = wed_opening_time if wed_opening_time.strip() else None
                thu_opening_time = thu_opening_time if thu_opening_time.strip() else None
                fri_opening_time = fri_opening_time if fri_opening_time.strip() else None
                sat_opening_time = sat_opening_time if sat_opening_time.strip() else None
                sun_opening_time = sun_opening_time if sun_opening_time.strip() else None
                
                mon_closing_time = mon_closing_time if mon_closing_time.strip() else None
                tue_closing_time = tue_closing_time if tue_closing_time.strip() else None
                wed_closing_time = wed_closing_time if wed_closing_time.strip() else None
                thu_closing_time = thu_closing_time if thu_closing_time.strip() else None
                fri_closing_time = fri_closing_time if fri_closing_time.strip() else None
                sat_closing_time = sat_closing_time if sat_closing_time.strip() else None
                sun_closing_time = sun_closing_time if sun_closing_time.strip() else None

            show_social_media_links = request.POST.get('show_social_media_links')
            if show_social_media_links:
                show_social_media_links = show_social_media_links.strip()

            if show_social_media_links:
                social_medias = request.POST.getlist('social_medias')
                social_links = request.POST.getlist('social_links')

            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            try:
                type = get_object_or_404(CscNameType, slug = type.strip())
            except Http404:
                messages.error(request, 'Invalid CSC Name Type')
                return redirect(self.redirect_url)

            try:
                state = get_object_or_404(State, state = state.strip())
            except Http404:
                messages.error(request, 'Invalid State')
                return redirect(self.redirect_url)

            try:
                district = get_object_or_404(District, district = district.strip())
            except Http404:
                messages.error(request, 'Invalid District')
                return redirect(self.redirect_url)
            
            try:
                block = get_object_or_404(Block, block = block.strip())
            except Http404:
                messages.error(request, 'Invalid Block')
                return redirect(self.redirect_url)
            
            self.object = CscCenter.objects.create(
                name = name.strip() if name else None, type = type, csc_reg_no = csc_reg_no.strip() if csc_reg_no else None, 
                state = state, district = district, block = block, location = location.strip() if location else None,
                zipcode = zipcode.strip() if zipcode else None, landmark_or_building_name = landmark_or_building_name.strip() if landmark_or_building_name else None,
                street = street.strip() if street else None, logo = logo, description = description.strip() if description else None, contact_number = contact_number.strip() if contact_number else None,
                owner = owner.strip() if owner else None, email = email.strip() if email else None, website = website.strip() if website else None, 
                mobile_number = mobile_number.strip() if mobile_number else None, whatsapp_number = whatsapp_number.strip() if whatsapp_number else None,
                mon_opening_time = mon_opening_time, tue_opening_time = tue_opening_time, 
                wed_opening_time = wed_opening_time, thu_opening_time = thu_opening_time, 
                fri_opening_time = fri_opening_time, sat_opening_time = sat_opening_time, 
                sun_opening_time = sun_opening_time, mon_closing_time = mon_closing_time, 
                tue_closing_time = tue_closing_time, wed_closing_time = wed_closing_time, 
                thu_closing_time = thu_closing_time, fri_closing_time = fri_closing_time, 
                sat_closing_time = sat_closing_time, sun_closing_time = sun_closing_time, 
                latitude = latitude.strip() if latitude else None, longitude = longitude.strip() if longitude else None
            )               
            
            # after creation of object
            self.object.keywords.set(keywords)
            self.object.services.set(services)
            self.object.products.set(products)
            self.object.save()

            if banners:
                for banner in banners:
                    banner_obj, created = Banner.objects.get_or_create(csc_center = self.object, banner_image = banner)
                    self.object.banners.add(banner_obj)
                self.object.save()

            if social_medias and social_links:
                social_media_length = len(social_medias)
                if social_media_length > 0:
                    social_media_list = []
                    for i in range(social_media_length):
                        if social_medias[i] and social_links[i]:
                            social_media_link, created = SocialMediaLink.objects.get_or_create(
                                csc_center_id = self.object,
                                social_media_name = social_medias[i].strip(),
                                social_media_link = social_links[i].strip()
                            )
                            social_media_list.append(social_media_link)
                    
                        self.object.social_media_links.set(social_media_list)
                        self.object.save()

            messages.success(request, "Added CSC center")
            if not User.objects.filter(email = email).exists():            
                return redirect(reverse('authentication:user_registration', kwargs={'email': self.object.email}))         
            
            return redirect(self.success_url)
        except Exception as e:
            msg = "Failed to add csc center"
            logger.exception(f"{msg}: {e}")
            messages.error(request, msg)
            return redirect(self.redirect_url)


class DetailCscCenterView(BaseAdminCscCenterView, DetailView):
    template_name = "admin_csc_center/detail.html"
    context_object_name = 'center'


class UpdateCscCenterView(BaseAdminCscCenterView, UpdateView):
    template_name = 'admin_csc_center/update.html'
    context_object_name = 'center'
    fields = "__all__"
    slug_url_kwarg = 'slug'
    redirect_url = reverse_lazy('csc_admin:csc_centers')

    def get_object(self, **kwargs):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid CSC Center")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception("Error in getting csc center object: %s", e)
            return redirect(self.redirect_url)
        
    def get_success_url(self):
        try:
            return reverse_lazy('csc_admin:csc_center', kwargs = {'slug': self.kwargs.get('slug')})
        except Exception as e:
            logger.exception("Error in getting success url of update csc center view: %s", e)
            return redirect(self.redirect_url)
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception("Error in getting redirect url of update csc center view: %s", e)
            return redirect(self.redirect_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['name_types'] = CscNameType.objects.all().order_by('type')
            context['keywords'] = CscKeyword.objects.all().order_by('keyword')
            context['products'] = Product.objects.all()
            context['states'] = State.objects.all()
            context['social_medias'] = ["Facebook", "Instagram", "Twitter", "YouTube", "LinkedIn", "Pinterest", "Tumblr"]
            self.object = self.get_object()
            context['selected_districts'] = District.objects.filter(state = self.object.state)
            context['selected_blocks'] = Block.objects.filter(district = self.object.district)

            time_data = []
            for i in range(1, 25):
                if i < 13:
                    str_time = f"{i} AM"
                else:
                    str_time = f"{i-12} PM"            
                time = datetime.strptime(str_time, "%I %p").strftime("%H:%M")
                time_data.append({"str_time": str_time, "time": time})
                context['time_data'] = time_data

        except Exception as e:
            logger.exception("Error in getting context data of update csc center view: %s", e)

        return context
    
    def post(self, request, *args, **kwargs):        
        try:
            name = request.POST.get('name')
            type = request.POST.get('type')
            csc_reg_name = request.POST.get('csc_reg_name')
            keywords = request.POST.getlist('keywords')

            state = request.POST.get('state')
            district = request.POST.get('district')
            block = request.POST.get('block')
            location = request.POST.get('location')
            zipcode = request.POST.get('zipcode')
            landmark_or_building_name = request.POST.get('landmark_or_building_name')
            street = request.POST.get('address')
            logo = request.FILES.get('logo')
            banners = request.FILES.getlist('banner')
            description = request.POST.get('description')
            owner = request.POST.get('owner')
            website = request.POST.get('website')
            contact_number = request.POST.get('contact_number')
            mobile_number = request.POST.get('mobile_number')
            whatsapp_number = request.POST.get('whatsapp_number')        
            services = request.POST.getlist('services')
            products = request.POST.getlist('products')

            show_opening_hours = request.POST.get('show_opening_hours')
            
            show_opening_hours = show_opening_hours.strip() if show_opening_hours else None

            if show_opening_hours:
                mon_opening_time = request.POST.get('mon_opening_time')
                tue_opening_time = request.POST.get('tue_opening_time')
                wed_opening_time = request.POST.get('wed_opening_time')
                thu_opening_time = request.POST.get('thu_opening_time')
                fri_opening_time = request.POST.get('fri_opening_time')
                sat_opening_time = request.POST.get('sat_opening_time')
                sun_opening_time = request.POST.get('sun_opening_time')

                mon_closing_time = request.POST.get('mon_closing_time')
                tue_closing_time = request.POST.get('tue_closing_time')
                wed_closing_time = request.POST.get('wed_closing_time')
                thu_closing_time = request.POST.get('thu_closing_time')
                fri_closing_time = request.POST.get('fri_closing_time')
                sat_closing_time = request.POST.get('sat_closing_time')
                sun_closing_time = request.POST.get('sun_closing_time')

                mon_opening_time = mon_opening_time.strip() if mon_opening_time else None
                tue_opening_time = tue_opening_time.strip() if tue_opening_time else None
                wed_opening_time = wed_opening_time.strip() if wed_opening_time else None
                thu_opening_time = thu_opening_time.strip() if thu_opening_time else None
                fri_opening_time = fri_opening_time.strip() if fri_opening_time else None
                sat_opening_time = sat_opening_time.strip() if sat_opening_time else None
                sun_opening_time = sun_opening_time.strip() if sun_opening_time else None
                
                mon_closing_time = mon_closing_time.strip() if mon_closing_time else None
                tue_closing_time = tue_closing_time.strip() if tue_closing_time else None
                wed_closing_time = wed_closing_time.strip() if wed_closing_time else None
                thu_closing_time = thu_closing_time.strip() if thu_closing_time else None
                fri_closing_time = fri_closing_time.strip() if fri_closing_time else None
                sat_closing_time = sat_closing_time.strip() if sat_closing_time else None
                sun_closing_time = sun_closing_time.strip() if sun_closing_time else None

            show_social_media_links = request.POST.get('show_social_media_links')

            show_social_media_links = show_social_media_links.strip() if show_social_media_links else None

            if show_social_media_links:
                social_medias = request.POST.getlist('social_medias')
                social_links = request.POST.getlist('social_links')

            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            try:
                type = get_object_or_404(CscNameType, slug = type.strip())
            except Http404:
                messages.error(request, 'Invalid CSC Name Type')
                return redirect(reverse_lazy('users:add_csc'))

            try:
                state = get_object_or_404(State, state = state.strip())
            except Http404:
                messages.error(request, 'Invalid State')
                return redirect(reverse_lazy('users:add_csc'))

            try:
                district = get_object_or_404(District, district = district.strip())
            except Http404:
                messages.error(request, 'Invalid District')
                return redirect(reverse_lazy('users:add_csc'))
            
            try:
                block = get_object_or_404(Block, block = block.strip())
            except Http404:
                messages.error(request, 'Invalid Block')
                return redirect(reverse_lazy('users:add_csc'))
            
            self.object = self.get_object()

            if name:
                self.object.name = name.strip()
            if type:
                self.object.type = type
            self.object.csc_reg_no = csc_reg_name.strip() if csc_reg_name else None
            if state:
                self.object.state = state
            if district:
                self.object.district = district
            if block:
                self.object.block = block
            if location:
                self.object.location = location.strip()
            if zipcode:
                self.object.zipcode = zipcode.strip()
            if landmark_or_building_name:
                self.object.landmark_or_building_name = landmark_or_building_name.strip()
            if street:
                self.object.street = street.strip()
                
            if logo:
                self.object.logo = logo

            if banners:
                for banner in banners:
                    banner_obj, created = Banner.objects.get_or_create(csc_center = self.object, banner_image = banner)
                    self.object.banners.add(banner_obj)

            if description:
                self.object.description = description.strip()
            if owner:
                self.object.owner = owner.strip()
                            
            self.object.website = website.strip() if website else None
            if contact_number:
                self.object.contact_number = contact_number.strip()
            if mobile_number:
                self.object.mobile_number = mobile_number.strip()
            if whatsapp_number:
                self.object.whatsapp_number = whatsapp_number.strip()

            self.object.show_opening_hours = True if show_opening_hours else False
            self.object.show_social_media_links = True if show_social_media_links else False

            if show_opening_hours:
                self.object.mon_opening_time = mon_opening_time.strip() if mon_opening_time else None
                self.object.tue_opening_time = tue_opening_time.strip() if tue_opening_time else None
                self.object.wed_opening_time = wed_opening_time.strip() if wed_opening_time else None
                self.object.thu_opening_time = thu_opening_time.strip() if thu_opening_time else None
                self.object.fri_opening_time = fri_opening_time.strip() if fri_opening_time else None
                self.object.sat_opening_time = sat_opening_time.strip() if sat_opening_time else None
                self.object.sun_opening_time = sun_opening_time.strip() if sun_opening_time else None
                self.object.mon_closing_time = mon_closing_time.strip() if mon_closing_time else None
                self.object.tue_closing_time = tue_closing_time.strip() if tue_closing_time else None
                self.object.wed_closing_time = wed_closing_time.strip() if wed_closing_time else None
                self.object.thu_closing_time = thu_closing_time.strip() if thu_closing_time else None
                self.object.fri_closing_time = fri_closing_time.strip() if fri_closing_time else None
                self.object.sat_closing_time = sat_closing_time.strip() if sat_closing_time else None
                self.object.sun_closing_time = sun_closing_time.strip() if sun_closing_time else None


            self.object.latitude = latitude.strip() if latitude else None
            self.object.longitude = longitude.strip() if longitude else None
            
            self.object.keywords.set(keywords)
            self.object.services.set(services)
            self.object.products.set(products)
            self.object.save()

            if social_medias and social_links:
                social_media_length = len(social_medias)
                if social_media_length > 0:
                    social_media_list = []
                    for i in range(social_media_length):
                        if social_medias[i] and social_links[i]:
                            social_media_link, created = SocialMediaLink.objects.get_or_create(
                                csc_center_id = self.object,
                                social_media_name = social_medias[i].strip(),
                                social_media_link = social_links[i].strip()
                            )
                            social_media_list.append(social_media_link)
                    
                        self.object.social_media_links.set(social_media_list)
                        self.object.save()
                else:
                    self.object.social_media_links.clear()
                    self.object.save()
            else:
                self.object.social_media_links.clear()
                self.object.save()

            messages.success(request, "Updated CSC Center Details")      
            
            return redirect(self.get_success_url())
        except Exception as e:
            msg = "Error in updating csc center"
            logger.exception(f"{msg}: {e}")
            messages.error(request, msg)
            return redirect(self.redirect_url)
    
    def form_invalid(self, form):
        try:
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error on field - {field}: {error}")
            return super().form_invalid(form)
        except Exception as e:
            logger.exception("Error in updating csc center: %s", e)


class DeleteCscCenterView(BaseAdminCscCenterView, View):
    success_url = reverse_lazy('csc_admin:csc_centers')
    redirect_url = success_url

    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(CscCenter, slug = kwargs['slug'])
        
            self.object.delete()
            messages.success(request, "Deleted CSC Center")
            return redirect(self.success_url)
    
        except Http404:
            messages.error(request, 'Invalid CSC Center')
            return redirect(self.redirect_url)
    
        except Exception as e:            
            logger.exception("Error in deleting csc center: %s", e)
            messages.error(request, "Error in deleting csc center")
            return redirect(self.redirect_url)


class RemoveCscCenterLogoView(BaseAdminCscCenterView, UpdateView):
    fields = ["logo"]
    pk_url_kwarg = 'slug'

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            self.object.logo = None
            self.object.save()
            return JsonResponse({'message': 'success'})
        except Exception as e:
            logger.exception("Error in removing csc center logo: %s", e)
            return JsonResponse({'message': 'Error in removing csc center logo'})

    
class RemoveCscCenterBannerView(BaseAdminCscCenterView, UpdateView):
    fields = ["banner"]
    pk_url_kwarg = 'slug'

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            self.object.banner = None
            self.object.save()
            return JsonResponse({'message': 'success'})
        except Exception as e:
            logger.exception("Error in removing csc center banner: %s", e)
            return JsonResponse({'message': 'Error in removing csc center banner'})


class RemoveSocialMediaLinkView(BaseAdminCscCenterView, UpdateView):
    fields = ["social_media_links"]
    pk_url_kwarg = 'slug'

    def get_object(self, **kwargs):
        try:
            return get_object_or_404(CscCenter, slug = self.kwargs['slug'])
        except Http404:
            return JsonResponse({"message": "Error. Invalid CSC Center"})
        except Exception as e:
            logger.exception("Error in getting csc center object: %s", e)
            return JsonResponse({"message": "Error in getting csc center object"})

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            social_media_id = request.POST.get('social_media_id').strip()
            
            try:
                social_media_link = get_object_or_404(SocialMediaLink, pk = social_media_id)
            except Http404:
                return JsonResponse({"message": "Error. No such social media object"})
            self.object.social_media_links.remove(social_media_link)
            self.object.save()

            return JsonResponse({'message': 'success'})
        except Exception as e:
            logger.exception("Error in removing social media link: %s", e)
            return JsonResponse({'message': 'Error in removing social media link'})
    

class CscOwnersListView(BaseAdminCscCenterView, ListView):
    queryset = CscCenter.objects.all().order_by("owner")
    template_name = "admin_csc_center/owners_list.html"
    context_object_name = 'csc_centers'
    paginate_by = 10    

    def get_queryset(self):
        try:
            unique_emails = set()
            unique_center_pks = []

            state = self.kwargs.get('state')
            district = self.kwargs.get('district')
            block = self.kwargs.get('block')
            
            queryset = self.queryset

            if state:
                queryset = queryset.filter(state__pk=state)
            if district:
                queryset = queryset.filter(district__pk=district)
            if block:
                queryset = queryset.filter(block__pk=block)

            for center in queryset:
                if center.email not in unique_emails:
                    unique_emails.add(center.email)
                    unique_center_pks.append(center.pk)

            return queryset.filter(pk__in=unique_center_pks)
        
        except Exception as e:
            logger.exception("Error in getting csc center queryset: %s", e)
            return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            state = self.kwargs.get('state')
            district = self.kwargs.get('district')
            block = self.kwargs.get('block')

            context['state'] = state if state else None

            context['districts'] = District.objects.filter(state__pk = state).order_by("district") if state else None
            context['district'] = district if district else None

            context['blocks'] = Block.objects.filter(state__id = state, district_id = district).order_by("block") if state and district else None
            context['block_id'] = block if block else None

        except Exception as e:
            logger.exception("Error in getting context data of csc owners list view: %s", e)

        return context


# Nuclear
class GetDistrictView(View):
    def get(self, request, *args, **kwargs):
        try:
            state_name = request.GET.get('state_name')
            districts = list(District.objects.filter(state__state=state_name).values())
            return JsonResponse({"districts": districts}, safe=False)
        except Exception as e:
            logger.exception("Error in getting districts: %s", e)
            return JsonResponse({"error": "Error in getting districts"})
        

class GetPopUpDistrictView(View):
    def get(self, request, *args, **kwargs):
        try:
            state_id = request.GET.get('state_id')
            districts = list(District.objects.filter(state__id=state_id).values())
            return JsonResponse({"districts": districts}, safe=False)
        except Exception as e:
            logger.exception("Error in getting districts: %s", e)
            return JsonResponse({"error": "Error in getting districts"})
    

class GetBlockView(View):
    def get(self, request, *args, **kwargs):
        try:
            district_name = request.GET.get('district_name')
            state_name = request.GET.get('state_name')
            blocks = list(Block.objects.filter(district__district = district_name, state__state = state_name).values())
            return JsonResponse({"blocks": blocks}, safe=False)
        except Exception as e:
            logger.exception("Error in getting blocks: %s", e)
            return JsonResponse({"error": "Error in getting blocks"})
    

# Json
def get_all_states(request):
    try:
        states = list(State.objects.all().order_by('state').values())
        return JsonResponse({"states": states}, safe=False)
    except Exception as e:
        logger.exception("Error in getting all states: %s", e)
        return JsonResponse({"error": "Error in getting all states"})

def get_all_districts(request):
    try:
        districts = list(District.objects.all().order_by('district').values())
        return JsonResponse({"districts": districts}, safe=False)
    except Exception as e:
        logger.exception("Error in getting all districts: %s", e)
        return JsonResponse({"error": "Error in getting all districts"})

def get_all_blocks(request):
    try:
        blocks = list(Block.objects.all().order_by('block').values())
        return JsonResponse({"blocks": blocks}, safe=False)
    except Exception as e:
        logger.exception("Error in getting all blocks: %s", e)
        return JsonResponse({"error": "Error in getting all blocks"})

def get_name_types(request):
    try:
        name_types = list(CscNameType.objects.all().order_by('type').values())
        return JsonResponse({"name_types": name_types}, safe=False)
    except Exception as e:
        logger.exception("Error in getting all name types: %s", e)
        return JsonResponse({"error": "Error in getting all name types"})
        

def get_csc_keywords(request):
    try:
        keywords = list(CscKeyword.objects.all().order_by('keyword').values())
        return JsonResponse({"keywords": keywords}, safe=False)
    except Exception as e:
        logger.exception("Error in getting all csc keywords: %s", e)
        return JsonResponse({"error": "Error in getting all csc keywords"})

class GetDistrictDetailsView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            district = get_object_or_404(District, pk = self.kwargs['pk'])
            return JsonResponse({"district": district.district, "state": district.state.state, "state_id": district.state.pk})
        except Http404:
            return JsonResponse({"error": "District not found"}, safe=False)
        except Exception as e:
            logger.exception("Error in getting district details: %s", e)
            return JsonResponse({"error": "Error in getting district details"})
        
    

class GetBlockDetailsView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            block = get_object_or_404(Block, pk = self.kwargs['pk'])
            return JsonResponse({
            "block": block.block,
            "state": block.state.state,
            "state_id": block.state.pk,
            "district": block.district.district,
            "district_id": block.district.pk
            })
        except Http404:
            return JsonResponse({"error": "Block not found"}, safe=False)
        except Exception as e:
            logger.exception("Error in getting block details: %s", e)
            return JsonResponse({"error": "Error in getting block details"})
        
        

# Geographic Views
class CreateStateView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            state = request.POST.get('state').title().strip()

            if not state:
                return JsonResponse({"error": "State is required"}, status=400)
            
            if not State.objects.filter(state = state).exists():
                State.objects.create(state = state)
                return JsonResponse({"status": "success"}, safe=False)
            else:
                return JsonResponse({"error": "State already exists"}, safe=False)
        except Exception as e:
            logger.exception("Error in creating state: %s", e)
            return JsonResponse({"error": "Error in creating state"})


class EditStateView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(State, pk = self.kwargs['pk'])
            state = request.POST.get('state').title().strip()

            if not state:
                return JsonResponse({"error": "State is required"}, status=400)        

            existing_state = State.objects.filter(state = state)
            if not existing_state.exists() or existing_state.first().pk == self.object.pk:        
                self.object.state = state
                self.object.save()
                return JsonResponse({"status": "success"}, safe=False)
            else:
                return JsonResponse({"error": "State already exists"}, safe=False)
            
        except Http404:
            return JsonResponse({"error": "State does not exist"}, status=400)
        except Exception as e:
            logger.exception("Error in updating state: %s", e)
            return JsonResponse({"error": "Error in updating state"})


class DeleteStateView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(State, pk = kwargs['pk'])
            self.object.delete()
            return JsonResponse({"status": "success"}, safe=False)    
        
        except Http404:
            return JsonResponse({"error": "Block does not exist"}, safe=False)
        
        except Exception as e:
            logger.exception("Error in deleting state: %s", e)
            return JsonResponse({"error": "Error in deleting state"})


class CreateDistrictView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            state = request.POST.get('state').strip()
            districts = request.POST.get('districts').strip()
            
            if not state:
                return JsonResponse({"error": "State is required"}, safe=False)
            
            try:
                state = get_object_or_404(State, pk = state)
            except Http404:
                return JsonResponse({"error": "State does not exist"}, safe=False)
            
            if not districts:
                return JsonResponse({"error": "District is required"}, safe=False)

            district_list = districts.split(",")        
            filtered_district_list = []
            for district in district_list:
                if re.match(r'^[a-zA-Z0-9 ]+$', district) and district.strip():
                    filtered_district_list.append(district)

            filtered_list_length = len(filtered_district_list)

            created_count = 0
            for district in filtered_district_list:
                district = district.strip().title()
                if not District.objects.filter(state = state, district = district).exists():
                    District.objects.create(state = state, district = district)
                    created_count += 1

            if created_count > 0:
                return JsonResponse({"status": "success"}, safe=False)
            else:
                if filtered_list_length > 1:
                    return JsonResponse({"error": f"Districts already exists for the state '{state}'"}, safe=False)
                else:
                    return JsonResponse({"error": f"District already exists for the state '{state}'"}, safe=False)
        except Exception as e:
            logger.exception("Error in creating district: %s", e)
            return JsonResponse({"error": "Error in creating district"})
            

class EditDistrictView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            try:
                self.object = get_object_or_404(District, pk = kwargs['pk'])
            except Http404:
                return JsonResponse({"error": "District does not exist"}, safe=False)

            state = request.POST.get('state').strip()
            district = request.POST.get('district').title().strip()
            
            if not state:
                return JsonResponse({"error": "State is required"}, safe=False)
            
            if not district:
                return JsonResponse({"error": "District is required"}, safe=False)
            
            try:
                state = get_object_or_404(State, pk = state)
            except Http404:
                return JsonResponse({"error": "State does not exist"}, safe=False)        
            
            existing_district = District.objects.filter(state = state, district = district)
            if not existing_district.exists() or existing_district.first().pk == self.object.pk:            
                self.object.state = state
                self.object.district = district
                self.object.save()
                return JsonResponse({"status": "success"}, safe=False)        
            else:            
                return JsonResponse({"error": f"District already exists for the state '{state}'"}, safe=False)
        except Exception as e:
            logger.exception("Error in updating district: %s", e)
            return JsonResponse({"error": "Error in updating district"})
        

class DeleteDistrictView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(District, pk = kwargs['pk'])
            self.object.delete()
            return JsonResponse({"status": "success"}, safe=False)
    
        except Http404:
            return JsonResponse({"error": "District does not exist"}, safe=False)
        
        except Exception as e:
            logger.exception("Error in deleting district: %s", e)
            return JsonResponse({"error": "Error in deleting district"})


class CreateBlockView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            state = request.POST.get('state').strip()
            district = request.POST.get('district').strip()
            blocks = request.POST.get('blocks').strip()
            
            if not state:
                return JsonResponse({"error": "State is required"}, safe=False)
            
            try:
                state = get_object_or_404(State, pk = state)
            except Http404:
                return JsonResponse({"error": "State does not exist"}, safe=False)
            
            if not district:
                return JsonResponse({"error": "District is required"}, safe=False)
            
            try:
                district = get_object_or_404(District, pk = district)
            except Http404:
                return JsonResponse({"error": "District does not exist"}, safe=False)

            if not blocks:
                return JsonResponse({"error": "Block is required"}, safe=False)

            block_list = blocks.split(",")        
            filtered_block_list = []
            for block in block_list:
                if re.match(r'^[a-zA-Z0-9 ]+$', block) and block.strip():
                    filtered_block_list.append(block)

            filtered_list_length = len(filtered_block_list)

            created_count = 0
            for block in filtered_block_list:
                block = block.strip().title()
                if not Block.objects.filter(state = state, district = district, block = block).exists():
                    Block.objects.create(state = state, district = district, block = block)
                    created_count += 1

            if created_count > 0:
                return JsonResponse({"status": "success"}, safe=False)
            else:
                if filtered_list_length > 1:
                    return JsonResponse({"error": f"Blocks already exists for the district '{district}' of state '{state}'"}, safe=False)
                else:
                    return JsonResponse({"error": f"Block already exists for the district '{district}' of state '{state}'"}, safe=False)
        except Exception as e:
            logger.exception("Error in creating blocks: %s", e)
            return JsonResponse({"error": "Error in creating blocks"}, safe=False)
            

class EditBlockView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            try:
                self.object = get_object_or_404(Block, pk = kwargs['pk'])
            except Http404:
                return JsonResponse({"error": "Block does not exist"}, safe=False)

            state = request.POST.get('state').strip()
            district = request.POST.get('district').strip()
            block = request.POST.get('block').title().strip()
            
            if not state:
                return JsonResponse({"error": "State is required"}, safe=False)
            
            if not district:
                return JsonResponse({"error": "District is required"}, safe=False)
            
            if not block:
                return JsonResponse({"error": "Block is required"}, safe=False)
            
            try:
                state = get_object_or_404(State, pk = state)
            except Http404:
                return JsonResponse({"error": "State does not exist"}, safe=False)

            try:
                district = get_object_or_404(District, pk = district)
            except Http404:
                return JsonResponse({"error": "District does not exist"}, safe=False)

            existing_block = Block.objects.filter(state = state, district = district, block = block)
            if not existing_block.exists() or existing_block.first().pk == self.object.pk:    
                self.object.state = state
                self.object.district = district
                self.object.block = block
                self.object.save()
                return JsonResponse({"status": "success"}, safe=False)

            else:            
                return JsonResponse({"error": f"Block already exists for the district '{district}' of state '{state}'"}, safe=False)
        except Exception as e:
            logger.exception("Error in editing block: %s", e)
            return JsonResponse({"error": "Error in editing block"}, safe=False)
        

class DeleteBlockView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(Block, pk = kwargs['pk'])
            self.object.delete()
            return JsonResponse({"status": "success"}, safe=False)
        
        except Http404:
            return JsonResponse({"error": "Block does not exist"}, safe=False)
        
        except Exception as e:
            logger.exception("Error in deleting block: %s", e)
            return JsonResponse({"error": "Error in deleting block"}, safe=False)
    

# CSC modules
class CreateKeywordView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            keyword = request.POST.get('keyword').strip()

            if not keyword:
                return JsonResponse({"error": "Keyword is required"}, status=400)
            
            if not CscKeyword.objects.filter(keyword = keyword).exists():
                CscKeyword.objects.create(keyword = keyword)
                return JsonResponse({"status": "success"}, safe=False)
            else:
                return JsonResponse({"error": "Keyword already exists"}, safe=False)
        except Exception as e:
            logger.exception("Error in creating keyword: %s", e)
            return JsonResponse({"error": "Error in creating keyword"}, safe=False)
        

@method_decorator(csrf_exempt, name="dispatch")
class EditKeywordView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(CscKeyword, slug = self.kwargs['slug'])
            keyword = request.POST.get('keyword').strip()

            if not keyword:
                return JsonResponse({"error": "Keyword is required"}, status=400)        

            existing_keyword = CscKeyword.objects.filter(keyword = keyword)
            if not existing_keyword.exists() or existing_keyword.first().slug == self.object.slug:
                self.object.keyword = keyword
                self.object.save()
                return JsonResponse({"status": "success"}, safe=False)
            else:
                return JsonResponse({"error": "Keyword already exists"}, safe=False)
        
        except Http404:
            return JsonResponse({"error": "Keyword does not exist"}, status=400)
    
        except Exception as e:
            logger.exception("Error in editing keyword: %s", e)
            return JsonResponse({"error": "Error in editing keyword"}, safe=False)


class DeleteKeywordView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(CscKeyword, slug = kwargs['slug'])
            self.object.delete()
            return JsonResponse({"status": "success"}, safe=False)
    
        except Http404:
            return JsonResponse({"error": "Keyword does not exist"}, safe=False)
        
        except Exception as e:
            logger.exception("Error in deleting keyword: %s", e)
            return JsonResponse({"error": "Error in deleting keyword"}, safe=False)
    

@method_decorator(csrf_exempt, name="dispatch")
class CreateCscNameTypeView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            name_type = request.POST.get('name_type').strip()

            if not name_type:
                return JsonResponse({"error": "Name Type is required"}, status=400)
            
            if not CscNameType.objects.filter(type = name_type).exists():
                CscNameType.objects.create(type = name_type)
                return JsonResponse({"status": "success"}, safe=False)
            else:
                return JsonResponse({"error": "Name Type already exists"}, safe=False)
        except Exception as e:
            logger.exception("Error in creating name type: %s", e)
            return JsonResponse({"error": "Error in creating name type"}, safe=False)
        

@method_decorator(csrf_exempt, name="dispatch")
class EditCscNameTypeView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(CscNameType, slug = self.kwargs['slug'])
            name_type = request.POST.get('name_type').strip()

            if not name_type:
                return JsonResponse({"error": "Name Type is required"}, status=400)        

            existing_name_type = CscNameType.objects.filter(type = name_type)
            if not existing_name_type.exists() or existing_name_type.first().slug == self.object.slug:
                self.object.type = name_type
                self.object.save()
                return JsonResponse({"status": "success"}, safe=False)
            else:
                return JsonResponse({"error": "Name type already exists"}, safe=False)
        
        except Http404:
            return JsonResponse({"error": "Name Type does not exist"}, status=400)
        
        except Exception as e:
            logger.exception("Error in editing name type: %s", e)
            return JsonResponse({"error": "Error in editing name type"}, safe=False)

class DeleteCscNameTypeView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(CscNameType, slug = kwargs['slug'])        
            self.object.delete()
            return JsonResponse({"status": "success"}, safe=False)
    
        except Http404:
            return JsonResponse({"error": "Name type does not exist"}, safe=False)
        
        except Exception as e:
            logger.exception("Error in deleting name type: %s", e)
            return JsonResponse({"error": "Error in deleting name type"}, safe=False)
        
##################################### CSC CENTER END #####################################

class BasePosterView(BaseAdminView):
    model = Poster
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['poster_page'] = True
        except Exception as e:
            logger.exception("Error in getting admin base poster context: %s", e)

        return context
    

class PosterListView(BasePosterView, ListView):
    template_name = 'admin_poster/list.html'
    queryset = Poster.objects.all()
    context_object_name = 'posters'


class PosterDetailView(BasePosterView, DetailView):
    template_name = 'admin_poster/detail.html'
    context_object_name = 'poster'
    slug_url_kwarg = 'slug'

class CreatePosterView(BasePosterView, CreateView):
    fields = ["title", "poster", "state", "service"]
    template_name = 'admin_poster/create.html'
    success_url = reverse_lazy('csc_admin:posters')
    redirect_url = reverse_lazy('csc_admin:create_poster')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['states'] = State.objects.all()
        except Exception as e:
            logger.exception("Error in getting admin create poster context: %s", e)

        return context

    def post(self, request, *args, **kwargs):
        try:
            title = request.POST.get('title').strip()
            poster = request.FILES.get('poster')
            state_id = request.POST.get('state').strip()
            service_slug = request.POST.get('service').strip() 

            try:
                state = get_object_or_404(State, pk = state_id)
            except Http404:
                messages.error(request, 'Invalid State')
                return redirect(self.redirect_url)
            
            try:
                service = get_object_or_404(Service, slug = service_slug)
            except Http404:
                messages.error(request, 'Invalid Service')
                return redirect(self.redirect_url)

            if title:
                self.poster = self.model.objects.create(title = title, poster = poster, state = state, service = service)            
                messages.success(request, 'Added Poster')
                return redirect(self.success_url)
            else:
                messages.warning(request, 'Please provide the poster title.')
                return redirect(self.redirect_url)
        
        except Exception as e:
            logger.exception("Error in creating poster: %s", e)
            messages.error(request, "Error in creating poster")
            return redirect(self.redirect_url)
        

class DeletePosterView(BasePosterView, View):
    success_url = reverse_lazy('csc_admin:posters')
    redirect_url = success_url

    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs['slug'])
            self.object.delete()
            messages.success(request, "Poster Deleted.")
            return redirect(self.success_url)
        except Http404:
            messages.error(request, 'Invalid Poster')
            return redirect(self.redirect_url)
        
        except Exception as e:
            logger.exception("Error in fetching poster object: %s", e)
            messages.error(request, "Error in deleting poster")
            return redirect(self.redirect_url)
        

class UpdatePosterView(BasePosterView, UpdateView):
    fields = ["title", "poster", "state", "service"]
    template_name = 'admin_poster/update.html'
    success_url = reverse_lazy('csc_admin:posters')
    redirect_url = success_url
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['states'] = State.objects.all()
        except Exception as e:
            logger.exception("Error in fetching post update context: %s", e)
        
        return context

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            title = request.POST.get('title').strip()
            poster = request.FILES.get('poster')
            state_id = request.POST.get('state').strip()
            service_slug = request.POST.get('service').strip() 

            try:
                state = get_object_or_404(State, pk = state_id)
            except Http404:
                messages.error(request, 'Invalid State')
                return redirect(self.redirect_url)
            
            try:
                service = get_object_or_404(Service, slug = service_slug)
            except Http404:
                messages.error(request, 'Invalid Service')
                return redirect(self.redirect_url)

            if not title:
                messages.warning(request, 'Title is required.')            
                return redirect(self.redirect_url)
            
            if not state:
                messages.warning(request, 'State is required.')            
                return redirect(self.redirect_url)
            
            if not service:
                messages.warning(request, 'Service is required.')            
                return redirect(self.redirect_url)
            
            if not poster:
                poster = self.object.poster

            self.object.title = title
            self.object.poster = poster
            self.object.state = state
            self.object.service = service
            self.object.save()

            messages.success(request, 'Updated Poster')
            return redirect(self.get_success_url())
        
        except Exception as e:
            logger.exception("Error in updating post: %s", e)
            messages.error(request, 'Error in updating post')
            return redirect(self.redirect_url)
            

################# Profile ##############

class MyProfileView(BaseAdminView, TemplateView):
    model = User
    template_name = "admin_profile/my_profile.html"
    success_url = reverse_lazy('csc_admin:my_profile')
    redirect_url = success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["profile_page"] = True
        except Exception as e:
            logger.exception("Error in fetchin admin profile context data: %s", e)

        return context
    
    def get_object(self):
        try:
            return get_object_or_404(User, email = self.request.user.email)
        except Http404:
            messages.error(self.request, 'Unauthorized user')
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception("Error in fetching user object: %s", e)
            messages.error(self.request, "Error in fetchin user object")
            return redirect(self.redirect_url)


class UpdateProfileView(MyProfileView, UpdateView):        
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            image = request.FILES.get('image')
            name = request.POST.get('name').strip().title()
            phone = request.POST.get('phone').strip()
            email = request.POST.get('email').strip().lower()
            notes = request.POST.get('notes').strip()

            if not email:
                messages.error(request, "Email is required")
                return redirect(self.redirect_url)

            if name:
                name_parts = name.split(' ')

                first_name = name_parts[0] if len(name_parts) > 0 else None
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else None

                self.object.first_name = first_name
                self.object.last_name = last_name            
                self.object.notes = notes            

            
            if  phone.isnumeric():
                self.object.phone = phone
            
            if image:
                self.object.image = image

            self.object.save()

            current_email = self.object.email

            if email != current_email:
                user_csc_centers = CscCenter.objects.filter(email = current_email)
                for csc_center in user_csc_centers:
                    csc_center.email = email
                    csc_center.save()
                self.object.email = email
                self.object.save()

            messages.success(request, "Updated user profile details.")
            return redirect(self.get_success_url())
        except Exception as e:
            logger.exception("Error in updating profile details: %s", e)
            messages.error(request, "Error in updating profile details")
            return redirect(self.redirect_url)


class ChangePasswordView(MyProfileView, UpdateView):
    success_url = reverse_lazy('authentication:login')
    redirect_url = reverse_lazy('csc_admin:my_profile')

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            current_password = request.POST.get('current_password').strip()
            new_password = request.POST.get('new_password').strip()
            confirm_password = request.POST.get('confirm_password').strip()

            user = authenticate(request, username = request.user.username, password = current_password)

            if user is not None and new_password == confirm_password:
                self.object.set_password(new_password)
                self.object.save()
                messages.success(request, "Password Updated. Please login again with your new password")
                logout(request)
                return redirect(self.get_success_url())
            
            if user is None:
                error_msg = "The current password you entered is incorrect"
            elif new_password != confirm_password:
                error_msg = "New passwords are not matching"
            else:
                error_msg = "Something went wrong."

            messages.error(request, error_msg)
            return redirect(self.redirect_url)
        
        except Exception as e:
            logger.exception("Error in updating password: %s", e)
            messages.error(request, "Error in updating password")
            return redirect(self.redirect_url)
    


############# FAQ START ##############

class BaseFaqView(BaseAdminView, View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['faq_page'] = True
        except Exception as e:
            logger.exception("Error in fetching admin base faq context data")
            
        return context

class CreateFaqView(BaseFaqView, CreateView):
    model = Faq
    success_url = redirect_url = reverse_lazy('csc_admin:add_faq')
    fields = ["question", "answer"]
    template_name = "admin_faq/create.html"

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "FAQ created successfully")
            return response
        except Exception as e:
            logger.exception("Error in creating faq: %s", e)
            messages.error(self.request, "Error in creating faq")
            return redirect(self.redirect_url)
    
    def form_invalid(self, form):
        try:
            messages.error(self.request, "FAQ creation failed")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error on field - {field}: {error}")
            return super().form_invalid(form)
        except Exception as e:
            logger.exception("Error in creating faq: %s", e)
            messages.error(self.request, "Error in creating faq")
            return redirect(self.redirect_url)


class ListFaqView(BaseFaqView, ListView):
    model = Faq
    template_name = "admin_faq/list.html"
    context_object_name = "faqs"
    queryset = model.objects.all()


class FaqDetailView(BaseFaqView, DetailView):
    model = Faq
    template_name = "admin_faq/detail.html"
    context_object_name = "faq"
    slug_url_kwarg = 'slug'


class UpdateFaqView(BaseFaqView, UpdateView):
    model = Faq
    fields = ["question", "answer"]
    template_name = "admin_faq/update.html"
    context_object_name = "faq"
    slug_url_kwarg = 'slug'
    success_url = redirect_url = reverse_lazy('csc_admin:faqs')

    def get_success_url(self):
        try:
            return reverse_lazy('csc_admin:faq', kwargs={'slug': self.kwargs.get('slug')})
        except Http404:
            return reverse_lazy('csc_admin:faqs')
        except Exception as e:
            logger.exception("Error in getting success url of faq updation view: %s", e)
            return redirect(self.success_url)
            
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception("Error in getting redirect url of faq updation view: %s", e)
            return redirect(self.redirect_url)


    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "FAQ updated successfully")
            return response
        except Exception as e:
            logger.exception("Error in updating faq: %s", e)
            messages.error(self.request, "Error in updating faq")
            return redirect(self.get_redirect_url())

    
    def form_invalid(self, form):
        try:
            messages.error(self.request, "FAQ updation failed")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error on field - {field}: {error}")
            return super().form_invalid(form)
        except Exception as e:
            logger.exception("Error in updating faq: %s", e)
            messages.error(self.request, "Error in updating faq")
            return redirect(self.get_redirect_url())
    

class DeleteFaqView(BaseFaqView, View):
    model = Faq
    success_url = reverse_lazy('csc_admin:faqs')
    redirect_url = success_url

    def get_object(self):
        try:
            return get_object_or_404(Faq, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid FAQ")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception("Error in getting faq object: %s", e)
            messages.error(self.request, "Error in getting faq object")
            return redirect(self.redirect_url)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "FAQ deleted successfully")
            return redirect(self.success_url)
        except Exception as e:
            logger.exception("Error in deleting faq: %s", e)
            messages.error(request, "Error in deleting faq")
            return redirect(self.redirect_url)

############# FAQ END ##############

############### ENQUIRY START ###############

class EnquiryBaseView(BaseAdminView):
    model = Enquiry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['enquiry_page'] = True
        except Exception as e:
            logger.exception("Error in getting admin base enquiry context data: %s", e)

        return context


class EnquiryListView(EnquiryBaseView, ListView):
    template_name = 'admin_enquiry/list.html'
    queryset = Enquiry.objects.all()
    context_object_name = 'enquiries'


class DeleteEnquiryView(EnquiryBaseView, View):
    success_url = reverse_lazy('csc_admin:enquiries')
    redirect_url = success_url

    def get_object(self):
        try:
            return get_object_or_404(Enquiry, slug=self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Enquiry")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception("Error in getting enquiry object: %s", e)
            messages.error(self.request, "Error in getting enquiry object")
            return redirect(self.redirect_url)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Enquiry deleted successfully")
            return redirect(self.success_url)
        except Exception as e:
            logger.exception("Error in deleting enquiry: %s", e)
            messages.error(self.request, "Error in deleting enquiry")
            return redirect(self.redirect_url)

class CscCenterEnquiriesListView(EnquiryBaseView, ListView):
    model = CscCenter
    context_object_name = 'csc_centers'
    template_name = "admin_enquiry/list_centers_enquiries.html"

    def get_queryset(self):
        try:
            # data = []
            # for csc_center in CscCenter.objects.all():
            #     service_enquiries_count = UserServiceEnquiry.objects.filter(csc_center = csc_center).count()
            #     product_enquiries_count = UserProductEnquiry.objects.filter(csc_center = csc_center).count()
            #     if service_enquiries_count > 0 or product_enquiries_count > 0:
            #         data.append({
            #             'name': csc_center.full_name,
            #             'service_enquiries_count': UserServiceEnquiry.objects.filter(csc_center = csc_center).count(),
            #             'product_enquiries_count': UserProductEnquiry.objects.filter(csc_center = csc_center).count()
            #         })
            # return data
            data = (
                CscCenter.objects.annotate(
                    service_enquiries_count=Count('serviceenquiry', filter=Q(serviceenquiry__isnull=False)),
                    product_enquiries_count=Count('productenquiry', filter=Q(productenquiry__isnull=False))
                )
                .filter(Q(service_enquiries_count__gt=0) | Q(product_enquiries_count__gt=0))
                .values('name', 'service_enquiries_count', 'product_enquiries_count')
            )

            return list(data)
        except Exception as e:
            logger.exception("Error in getting csc centers enquiry list: %s", e)
            messages.error(self.request, "Error in getting csc centers enquiry list")
            return []
        
############### ENQUIRY END ###############

class PaymentHistoryBaseView(BaseAdminView):
    model = Payment

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        try:
            context['csc_center_page'] = True
        except Exception as e:
            logger.exception("Error in getting admin payment history context data: %s", e)

        return context

class PaymentHistoryListView(PaymentHistoryBaseView, ListView):
    queryset = Payment.objects.all().order_by('-created')
    template_name = "admin_csc_center/list_payment_history.html"
    ordering = ['-created']
    context_object_name = 'payments'
    paginate_by = 10




class PaymentHistoryDetailView(PaymentHistoryBaseView, DetailView):
    context_object_name = 'payment'
    template_name = "admin_csc_center/detail_payment_history.html"

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        try:
            service_charge = 50
            context['service_charge'] = service_charge
            self.object = self.get_object()
            context['total'] = self.object.amount + service_charge
        except Exception as e:
            logger.exception("Error in getting admin payment history context data: %s", e)

        return context
    

# Price
class AddPriceView(BaseAdminView, CreateView):
    model = Price
    fields = ("price", "from", "to", "description")

    def post(self, request, *args, **kwargs):
        try:
            if request.headers.get('X-Requested-With') == "XMLHttpRequest":
                price = request.POST.get("price")
                price = price.strip() if price else None
                from_date = request.POST.get("from")
                from_date = from_date.strip() if from_date else None
                to_date = request.POST.get("to")
                to_date = to_date.strip() if to_date else None
                description = request.POST.get("description")
                description = description.strip() if description else None

                if from_date and to_date:
                    starting_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                    ending_date = datetime.strptime(to_date, '%Y-%m-%d').date()                        
                    if starting_date < timezone.now().date() or ending_date < starting_date:
                        return JsonResponse({"error": "Invalid date range"}, status=400)
                    self.object = Price.objects.all().first() if Price.objects.all().count() > 0 else None  
                    price_obj = self.object


                    if self.object:                            
                        if self.object.offer_price == float(price) and self.object.from_date == starting_date and self.object.to_date == ending_date and self.object.description == description:
                            return JsonResponse({"error": "Price already exists"})
                                                    
                        self.object.offer_price = price
                        self.object.from_date = from_date
                        self.object.to_date = to_date
                        self.object.description = description
                        self.object.save()
                    else:
                        default_amount = 500
                        price_obj = Price.objects.create(price=default_amount, offer_price = price, from_date = from_date, to_date = to_date, description = description)                            

                    list_centers = CscCenter.objects.all().order_by("owner")        
                    for center in CscCenter.objects.all().order_by("owner"):
                        while list_centers.filter(email = center.email).count() > 1:
                            removing_center_pk = list_centers.filter(email = center.email).last().pk
                            list_centers = list_centers.exclude(pk = removing_center_pk)                                        

                    center = CscCenter.objects.get(name = "RBC")
                    send_offer_mail.delay(center, price_obj)
                    
                else:
                    for price_obj in Price.objects.all():
                        price_obj.delete()
                    Price.objects.create(price=price)
                    
                return JsonResponse({"status": "success"})
        except Exception as e:
            logger.exception("Error in adding price: %s", e)
            return JsonResponse({"status": "Error in adding price"})
        return super().post(request, *args, **kwargs)
