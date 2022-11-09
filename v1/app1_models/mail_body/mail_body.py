from django.db import models

from ..mail_object.mail_object import mailObject
from ..mail_head.mail_head import mailHead

class mailBody(models.Model):
        
    mail_body_id=models.AutoField(primary_key=True)
    body_url=models.CharField(null=True, max_length=300)
    body_draft_url=models.CharField(null=True, max_length=300)
    mailHead=models.OneToOneField(to=mailHead,on_delete=models.CASCADE,blank=True)
    mailObject=models.ForeignKey(
        to=mailObject,
        on_delete=models.CASCADE,
        db_constraint=True
        )
    
    
        
    def __str__(self):
        return self.mailHead.subject
        