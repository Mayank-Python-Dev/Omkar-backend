from datetime import date
from dateutil.relativedelta import relativedelta
from contract.models import (
    Rental as ContractRental
)
from superadmin.firebaseManager import (
    sendPush
)
from notification.models import (
    RentalNotification
)
from django.http import HttpResponse

current_date = date.today()
previous_date = date.today() + relativedelta(months=-3)


print("Hello World!")
# def check_contract_rental(request):
#     contract_rental = ContractRental.objects.filter(agreement_valid_end_date__range=[previous_date,current_date])
#     if contract_rental:
#         rental_instance = [RentalNotification(
#             rental_id = i.user.id ,
#             gala_id = i.gala.id,
#             message = f"Your gala {i.gala.gala_number}({i.gala.warehouse.property_name}) is about to expire! you can renew your contract by submitting a requesting for gala {i.gala.gala_number}"
# 	    ) for i in contract_rental]
#         RentalNotification.objects.bulk_update_or_create(rental_instance,['rental_id','gala_id','message'],match_field=['rental_id','gala_id','message'])
#     return HttpResponse('hello world')

