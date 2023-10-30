from django.contrib import admin
from .models import (
    Company,
    Property,
    Gala
)


class CompanyAdmin(admin.ModelAdmin):

    @admin.display(description = "created_at")
    def admin_created_at(self,instance):
        return instance.created_at.strftime("%d-%m-%Y %I:%M %p")
    
    @admin.display(description = "updated_at")
    def admin_updated_at(self,instance):
        return instance.updated_at.strftime("%d-%m-%Y %I:%M %p")

    list_display = ['uid','name','admin_created_at','admin_updated_at']

    class Meta:
        model = Company

class PropertyAdmin(admin.ModelAdmin):

    @admin.display(description = "created_at")
    def admin_created_at(self,instance):
        return instance.created_at.strftime("%d-%m-%Y %I:%M %p")
    
    @admin.display(description = "updated_at")
    def admin_updated_at(self,instance):
        return instance.updated_at.strftime("%d-%m-%Y %I:%M %p")

    list_display = ['uid','company','property_name','admin_created_at','admin_updated_at','is_allotted_to_farmer']
    class Meta:
        model = Property

class GalaAdmin(admin.ModelAdmin):

    @admin.display(description = "created_at")
    def admin_created_at(self,instance):
        return instance.created_at.strftime("%d-%m-%Y %I:%M %p")
    
    @admin.display(description = "updated_at")
    def admin_updated_at(self,instance):
        return instance.updated_at.strftime("%d-%m-%Y %I:%M %p")

    list_display = ['uid','warehouse','gala_number','gala_area_size','gala_price','admin_created_at','admin_updated_at','is_allotted','is_allotted_to_rental','is_allotted_to_farmer']
    class Meta:
        model = Gala


admin.site.register(Company, CompanyAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Gala, GalaAdmin)

