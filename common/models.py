# from django.db import models
# from account.models import (
#     User
# )

# from account.user_managers import (
#     UserManager
# )
# # Create your models here.

# class OwnerManager(UserManager):
#     def get_queryset(self):
#         return super(OwnerManager,self).get_queryset().filter(
#             groups__name='Owner')

# class Owner(User):
#     objects =OwnerManager()
#     class Meta:
#         proxy = True
#         verbose_name_plural= 'Owner'