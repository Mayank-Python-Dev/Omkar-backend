import django_filters

from contract.models import (
    Rental as ContractRental
)

class ContractRentalFilter(django_filters.FilterSet):
    user_type = django_filters.AllValuesFilter(field_name = "owner__groups__name",lookup_expr='iexact')
    class Meta:
        model = ContractRental
        fields = ['user_type']