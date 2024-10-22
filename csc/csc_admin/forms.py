from django import forms
from services.models import Service
from blog.models import Blog
from ckeditor.widgets import CKEditorWidget

class CreateServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["description"]

        widgets = {
            'description': CKEditorWidget(attrs={
                'name': 'description',
                'id': 'description'           
            }),            
        }

    class Media:
        js = (
            'ckeditor/ckeditor-init.js',
            'ckeditor/ckeditor/ckeditor.js',
        )

        
class UpdateServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["description"]

        widgets = {
            'description': CKEditorWidget(attrs={
                'name': 'description',
                'id': 'description'           
            }),            
        }

    class Media:
        js = (
            'ckeditor/ckeditor-init.js',
            'ckeditor/ckeditor/ckeditor.js',
        )


class CreateBlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["content"]

        widgets = {
            'content': CKEditorWidget(attrs={
                'name': 'content',
                'id': 'content',        
            }),            
        }

    class Media:
        js = (
            'ckeditor/ckeditor-init.js',
            'ckeditor/ckeditor/ckeditor.js',
        )


class UpdateBlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["content"]

        widgets = {
            'content': CKEditorWidget(attrs={
                'name': 'content',
                'id': 'content'           
            }),            
        }

    class Media:
        js = (
            'ckeditor/ckeditor-init.js',
            'ckeditor/ckeditor/ckeditor.js',
        )