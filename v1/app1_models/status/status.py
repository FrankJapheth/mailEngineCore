from django.db import models

from ..mail_accounts.mail_accounts import mailAccounts

class mailStatus(models.Model):
        
        status_id=models.AutoField(primary_key=True)
        status_name=models.CharField(null=True,max_length=100)
        account=models.ForeignKey(to=mailAccounts,on_delete=models.CASCADE,null=True)
        
        def __str__(self) :
            
            return self.status_name