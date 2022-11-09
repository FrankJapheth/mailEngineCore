from django.contrib import admin


from .app1_models.mail_accounts.mail_accounts import mailAccounts
from .app1_models.mail_body.mail_body import mailBody
from .app1_models.mail_head.mail_head import mailHead
from .app1_models.mail_object.mail_object import mailObject
from .app1_models.mail_attachments.mail_attachments import mailAttachments
from .app1_models.label.label import MailLabel
from .app1_models.status.status import mailStatus
from .app1_models.mail_user_accounts.mail_user_accounts import UserMailAccounts


# Register your models here.


admin.site.register(mailAccounts)
admin.site.register(mailStatus)
admin.site.register(mailObject)
admin.site.register(mailHead)
admin.site.register(mailAttachments)
admin.site.register(mailBody)
admin.site.register(MailLabel)
admin.site.register(UserMailAccounts)
