from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from .models import (
    Contract,
    Investor,
    Rental,
    Farmer
)

class ModelAChildAdmin(PolymorphicChildModelAdmin):

    base_model = Contract

@admin.register(Investor)
class ContractAdmin(ModelAChildAdmin):
    list_display = ['gala','owner','user','agreement_type']
    base_model = Investor  # Explicitly set here!
    show_in_index = True  # makes child model admin visible in main admin site

@admin.register(Rental)
class ContractAdmin(ModelAChildAdmin):
    list_display = ['gala','owner','user','locking_period','agreement_type','agreement_valid_end_date']
    base_model = Rental  # Explicitly set here!
    show_in_index = True  # makes child model admin visible in main admin site

@admin.register(Farmer)
class ContractAdmin(ModelAChildAdmin):
    list_display = ['warehouse','owner','user','agreement_type']
    base_model = Farmer  # Explicitly set here!
    show_in_index = True  # makes child model admin visible in main admin site


# @admin.register(Farmer)
# class ContractAdmin(ModelAChildAdmin):
#     base_model = Farmer  # Explicitly set here!
#     show_in_index = True  # makes child model admin visible in main admin site


@admin.register(Contract)
class ProductAdmin(PolymorphicParentModelAdmin):
    base_model = Contract  # Optional, explicitly set here.
    child_models = (Investor, Rental,Farmer)
