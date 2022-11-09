from django.db import models

class mailAccounts(models.Model):
    
    account_id = models.AutoField(primary_key=True)
    account_name=models.CharField(null=True, max_length=100)
    last_mail_id=models.CharField(null=True, max_length=50)
    
    def __str__(self):
        return self.account_name
        