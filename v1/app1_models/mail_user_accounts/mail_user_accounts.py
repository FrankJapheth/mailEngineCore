from django.db import models
from django.contrib.auth.models import User

class UserMailAccounts(models.Model):

    account_id=models.AutoField(primary_key=True)

    account_hostname=models.CharField(max_length=100)
    account_host_engine_adress=models.CharField(max_length=100)
    account_host_login_adress=models.CharField(max_length=100)
    account_host_login_password=models.CharField(max_length=100)
    account_inbox = models.IntegerField(default=0)
    account_outbox = models.IntegerField(default=0)

    account_user=models.ForeignKey(to=User, on_delete=models.CASCADE,null=True)

    def __str__(self) -> str:
        return self.account_hostname