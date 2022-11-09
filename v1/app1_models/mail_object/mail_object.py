from django.db import models

from ..mail_accounts.mail_accounts import mailAccounts
from ..mail_user_accounts.mail_user_accounts import UserMailAccounts

class mailObject(models.Model):        
        
    archived=models.BooleanField(default=False)
    mail_object_id=models.AutoField(primary_key=True)
    mail_type=models.CharField(null=True, max_length=100)
    system_mail=models.BooleanField(default=True)
    status=models.CharField(null=True, max_length=100)
    mail_label=models.CharField(null=True, max_length=100)
    mail_server_id= models.IntegerField(null=True)
    body=models.BooleanField(default=False)
    account=models.ForeignKey(to=mailAccounts,on_delete=models.CASCADE,null=True)
    user_account=models.ForeignKey(to=UserMailAccounts,on_delete=models.CASCADE,null=True)
    
    def __str__(self):
        
        return str(self.mail_object_id)