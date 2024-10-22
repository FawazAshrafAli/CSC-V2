from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Category
import logging

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def create_initial_services(sender, **kwargs):
    try:
        categories = ["Electronics", "Fashion and Apparel", "Home and Furniture", "Health and Beauty"]
        if sender.name == "products":
            for category in categories:
                if Category.objects.count() < 4:
                    if not Category.objects.filter(name=category).exists():
                        Category.objects.create(name=category)
                else:
                    break
    except Exception as e:
        logger.exception(f"Error creating initial categories: {e}")
