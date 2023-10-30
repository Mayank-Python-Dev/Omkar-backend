import uuid
from django.db import models
from account.models import User

# Create your models here.


class BaseModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TokenAuthentication(BaseModel):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    access = models.TextField()

    class Meta:
        verbose_name_plural = "Token Authentication"

    def __str__(self):
        return str(self.user.username)
    
