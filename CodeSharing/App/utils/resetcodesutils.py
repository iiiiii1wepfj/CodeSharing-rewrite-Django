from datetime import timedelta
from django.utils.timezone import now
from ..models import ResetCodes


def autodelcodes():
    ResetCodes.objects.filter(
        creation_date__lte=(now() - timedelta(minutes=30))
    ).delete()
