from django.db import models
from django.utils import timezone

from ..mail_head.mail_head import mailHead

class mailAttachments(models.Model):
        
    mail_attachment_id=models.AutoField(primary_key=True)
    file_url=models.CharField(null=True, max_length=400)
    mailHead=models.ForeignKey(to=mailHead,on_delete=models.CASCADE,blank=True)
    
    def __str__(self):
        return self.mailHead.subject