from django.contrib import admin
from .models import Request, Like, DisLike

# Register your models here.
@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'request', 'user', 'company', 'activity', 'date_created', 'is_active' )

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'request',)

@admin.register(DisLike)
class DisLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'request',)