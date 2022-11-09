from django.db import models

from ..mail_object.mail_object import mailObject

class mailHead(models.Model):
    
    sender=models.CharField(null=True, max_length=100)
    reply_to=models.CharField(null=True, max_length=100)
    recipient=models.CharField(null=True, max_length=100)
    recipient_email_address=models.CharField(null=True, max_length=100)
    subject=models.CharField(null=True, max_length=700)
    mail_date=models.CharField(null=True, max_length=100)
    att_present=models.BooleanField(default=False)
    mail_head_id=models.AutoField(primary_key=True)
    mailObject= models.ForeignKey(to=mailObject,on_delete=models.CASCADE,blank=True)
    
        
    def __str__(self):
        
        return self.subject
        