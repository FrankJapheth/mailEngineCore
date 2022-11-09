from django.db import models


class MailLabel(models.Model):
    
        label_id=models.AutoField(primary_key=True)
        lebel_name=models.CharField(null=True,max_length=100)
        
        def __str__(self):
                return  self.lebel_name