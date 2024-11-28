from django.core.management.base import BaseCommand
from datetime import datetime
import pytz
from csc_center.tasks import check_validty_for_old_centers

class Command(BaseCommand):
    help = 'Schedule the validity checking function of old cscs'

    def handle(self, *args, **kwargs):
        india_timezone = pytz.timezone('Asia/Kolkata')
        local_eta = india_timezone.localize(datetime(2024, 12, 30, 0, 0))
        utc_eta = local_eta.astimezone(pytz.utc)
        
        check_validty_for_old_centers.apply_async(args=[], eta=utc_eta)
        
        self.stdout.write(
            self.style.SUCCESS(f'Task scheduled successfully for {local_eta.strftime("%Y-%m-%d %H:%M:%S %Z")}')
        )