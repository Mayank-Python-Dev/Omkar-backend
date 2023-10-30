from django.contrib import admin
from .models import (
    User,
    Rental,
    Investor,
    Farmer,
    UserAndInvestor,
    Owner
)


class UserAdmin(admin.ModelAdmin):
    
    @admin.display(description="belong_to")
    def admin_belong_to(self,instance):
        return ", ".join(_.name for _ in instance.belong_to.all())

    list_display = ['user_uid','username','email','is_superuser','is_staff','is_active','admin_belong_to']


    class Meta:
        model = User

class RentalAdmin(admin.ModelAdmin):

    @admin.display(description="belong_to")
    def admin_belong_to(self,instance):
        return ", ".join(_.name for _ in instance.belong_to.all())

    list_display = ['user_uid','username','email','is_superuser','is_staff','is_active','admin_belong_to']

    class Meta:
        model = Rental

class InvestorAdmin(admin.ModelAdmin):

    @admin.display(description="belong_to")
    def admin_belong_to(self,instance):
        return ", ".join(_.name for _ in instance.belong_to.all())

    list_display = ['user_uid','username','email','is_superuser','is_staff','is_active','admin_belong_to']


    class Meta:
        model = Investor

class FarmerAdmin(admin.ModelAdmin):

    @admin.display(description="belong_to")
    def admin_belong_to(self,instance):
        return ", ".join(_.name for _ in instance.belong_to.all())

    list_display = ['user_uid','username','email','is_superuser','is_staff','is_active','admin_belong_to']


    class Meta:
        model = Farmer


class UserInvestorAdmin(admin.ModelAdmin):

    @admin.display(description="belong_to")
    def admin_belong_to(self,instance):
        return ", ".join(_.name for _ in instance.belong_to.all())

    list_display = ['user_uid','username','email','is_superuser','is_staff','is_active','admin_belong_to']


    class Meta:
        model = UserAndInvestor

class OwnerAdmin(admin.ModelAdmin):

    list_display = ['user_uid','username','email','is_superuser','is_staff','is_active']


    class Meta:
        model = Owner

admin.site.register(User,UserAdmin)
admin.site.register(Rental,RentalAdmin)
admin.site.register(Investor,InvestorAdmin)
admin.site.register(Farmer,FarmerAdmin)
admin.site.register(Owner,OwnerAdmin)
admin.site.register(UserAndInvestor,UserInvestorAdmin)

