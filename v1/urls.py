from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views


urlpatterns=[
    path('createUser',views.creatAccount,name='createUser'),
    path('authenticateUser',views.authenticateUser,name='authenticateUser'),
    path('uploadFile',views.uploadFile,name='uploadFile'),
    path('fetchMailHeads',views.get_mail_heads,name="fetchMailHeads"),
    path('fetchMail',views.get_mail,name='fetchMail'),
    path('sendMail',views.send_mail,name="sendMail"),
    path('getAtt',views.get_att,name="getAtt"),
    path('getDraftBody',views.get_editable_mail_body,name="getDraftBody"),
    path('markSpam',views.spamMail,name="markSpam"),
    path('markArchive',views.archiveMail,name="markArchive"),
    path('unMarkArchive',views.unArchiveMail,name="unMarkArchive"),
    path('markTrash',views.trashMail,name="markTrash"),
    path('unMarkSpam',views.unSpamMail,name="unMarkSpam"),
    path('unMarkTrash',views.unTrashMail,name="unMarkTrash"),
    path('clearBox',views.clear_box,name="clearBox"),
    path('createMailAccount',views.create_user_mail_account,name="createMailAccount"),
    path('getMailAccounts',views.get_mail_accounts,name="getMailAccounts"),
]
urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)