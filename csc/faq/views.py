from django.views.generic import ListView

from .models import Faq

class FaqListView(ListView):
    model = Faq
    queryset = model.objects.all()
    template_name = 'faq/list.html'
    context_object_name = "faqs"