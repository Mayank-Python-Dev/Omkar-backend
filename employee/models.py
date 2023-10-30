import uuid
from django.db import models

# Create your models here.


class BaseModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Employee(BaseModel):
    name  = models.CharField(max_length=50)
    contact_no = models.CharField(max_length=50)
    # designation : Designation will be service which has m2m relation so will add this field after confirmation
    address = models.TextField()
    city = models.CharField(max_length=26)
    zipcode = models.CharField(max_length=26)
    # notes : not sure about note

    def __str__(self):
        return self.name.title()
    
    class Meta:
        ordering = ('-created_at',)
        verbose_name_plural = "Employee"
