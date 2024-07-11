from django.contrib import admin
from .models import File, Comment, ResetCodes


# Register your models here.
admin.site.register(File)
admin.site.register(Comment)
admin.site.register(ResetCodes)
