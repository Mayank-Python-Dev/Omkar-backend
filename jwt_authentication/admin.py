from django.contrib import admin
from .models import (
    TokenAuthentication
)
# Register your models here.

class TokenAuthenticationAdmin(admin.ModelAdmin):

    list_display = ['uid','user','access','created_at','updated_at']

admin.site.register(TokenAuthentication,TokenAuthenticationAdmin)
