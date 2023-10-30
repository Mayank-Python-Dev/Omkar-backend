from django.core.management.base import BaseCommand
from datetime import date,datetime
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
current_date_with_formatter = datetime.strptime(str(current_date),"%Y-%m-%d").strftime("%d %b,%Y")
next_date = date.today() + relativedelta(months=+3)
next_date_with_formatter = datetime.strptime(str(next_date),"%Y-%m-%d").strftime("%d %b,%Y")

class Command(BaseCommand):
    help = "This command is for running cronjob ..."

    def handle(self, *args, **kwargs):
        contract_rental = ContractRental.objects.filter(agreement_valid_end_date=next_date).values(
                    "user_id","gala_id","gala__gala_number","gala__warehouse__property_name"
        )
        if contract_rental:
            rental_instance = [RentalNotification(
                rental_id = i['user_id'],
                gala_id = i['gala_id'],
                status = "Renew_Gala",
                message = f"Your gala {i['gala__gala_number']}({i['gala__warehouse__property_name']}) is about to expire on {next_date_with_formatter}! you can renew your contract by submitting a requesting for gala {i['gala__gala_number']}"
            ) for i in contract_rental]
            RentalNotification.objects.bulk_update_or_create(rental_instance,['rental_id','gala_id','message'],match_field=['rental_id','gala_id','message'])
            contract_instance = ContractRental.objects.filter(agreement_valid_end_date=next_date).values(
                "user_id","gala_id","gala__gala_number","gala__warehouse__property_name","user__fcmdevice__registration_id"
            )
            for instance in contract_instance:
                sendPush("Renew Contract",f"Your gala {instance['gala__gala_number']}({instance['gala__warehouse__property_name']}) is about to expire on {next_date_with_formatter}! you can renew your contract by submitting a requesting for gala {instance['gala__gala_number']}",["cTSP-ZadSgqdRUJJycpyJz:APA91bFrWdkzkpkx6Qdk_PKeFzt3mM0OVfj1YPNWDmfj7eJag4b33ErFjVYFTH90BPsQjB7MKTPpx1vIEYdH_nciKANPyzQvlg0lo2DLqDxk0RR7DsLqa6rmfKESQyZKN_1RbbbmfmlY"])
            self.stdout.write("Rental Notification is updated!")
        self.stdout.write("Hello World!")