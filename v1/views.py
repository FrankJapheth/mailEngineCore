import json
import os

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.conf import settings
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.utils import timezone

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .app1_core.mails_core.receiver import MailReciever
from .app1_core.mails_core.sender import MailSender

from .app1_models.mail_object.mail_object import mailObject
from .app1_models.mail_head.mail_head import mailHead
from .app1_models.mail_accounts.mail_accounts import mailAccounts
from .app1_models.mail_attachments.mail_attachments import mailAttachments
from .app1_models.mail_body.mail_body import mailBody
from .app1_models.status.status import mailStatus
from .app1_models.label.label import MailLabel
from .app1_models.mail_user_accounts.mail_user_accounts  import UserMailAccounts


smtp_engine_port=465
imap_engine_port=995

class MailResp(Response):

    def close(self):
        super(MailResp,self).close()
        if self.status_code ==  200:
            return

def handle_uploaded_file(f):
    try:

        with open(settings.MEDIA_ROOT+'/temp/'+f.name, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
            return os.path.abspath(settings.MEDIA_ROOT+'/temp/'+f.name)
    except FileExistsError:
        return 'file does not exist'

def json_resp(resp_data):
    infos={ 'backendResponse':resp_data }
    resp=JsonResponse(infos,safe=False)
    resp["Access-Control-Allow-Origin"]="*"
    resp["respType"]="normal"
    resp["Author"] = "adedefranklyne@gmail.com"
    resp["Access-Control-Expose-Headers"]="respType"
    return resp


@api_view(["POST"])
def creatAccount(request):
    request_data=request.data
    user_email=request_data["userEmail"]
    user_name=request_data["userName"]
    user_password=request_data["userPassword"]

    try:
        user:User=User.objects.create_user(username=user_email,first_name=user_name,email=user_email,password=user_password)
        user.first_name=request_data["userName"]
        user.save()

        mail_accounts=mailAccounts.objects.all()
        m_accounts=[]
        for mail_account in mail_accounts:
            m_accounts.append(mail_account.account_name)
        mail_response=json_resp([0,'Sign Up successful',user.username,m_accounts,user.first_name])
    except IntegrityError:
        mail_response=json_resp([1,'Already in system just sign in'])

    return mail_response

@api_view(["POST"])
def authenticateUser(request):
    request_data=request.data
    user_email=request_data["userEmail"]
    user_password=request_data["userPassword"]
    user = authenticate(username=user_email, password=user_password)
    if user is not None:
        mail_lables=MailLabel.objects.all()
        mail_accounts=mailAccounts.objects.all()
        m_accounts=[]
        for mail_account in mail_accounts:
            account_object={}
            account_statuses_to_send=[]
            account_statuses=mailStatus.objects.filter(account__account_name=mail_account.account_name)
            for account_status in account_statuses:
                account_statuses_to_send.append(account_status.status_name)
            account_object[mail_account.account_name]=account_statuses_to_send
            m_accounts.append(account_object)

        labels_to_send=[]

        for mail_label in mail_lables:
            labels_to_send.append(mail_label.lebel_name)

        mail_response=json_resp([0,'Sign In successful',user.username,m_accounts,user.first_name,labels_to_send])
    else:
        mail_response=json_resp([1,'Sign In failed'])

    return mail_response

@api_view(['POST'])
def create_user_mail_account(request):

    request_data=request.data
    user_contact=request_data['userContact']
    hostname=request_data['hostname']
    engineAddress=request_data['engineAddress']
    logInAdress=request_data['logInAdress']
    logInPassword=request_data['logInPassword']

    account_user = User.objects.get(username=user_contact)

    user_mail_account:UserMailAccounts=UserMailAccounts()

    user_mail_account.account_host_engine_adress=engineAddress
    user_mail_account.account_host_login_adress=logInAdress
    user_mail_account.account_host_login_password=logInPassword
    user_mail_account.account_hostname=hostname
    user_mail_account.account_user=account_user

    user_mail_account.save()

    return json_resp('success')

@api_view(['POST'])
def get_mail_accounts(request):

    request_data=request.data
    user_contact=request_data['userContact']

    user_mail_accounts =UserMailAccounts.objects.filter(account_user__username=user_contact)

    user_mail_accounts_to_send = []

    if len(user_mail_accounts)>0:

        for user_mail_account in user_mail_accounts:

            user_mail_account_to_send = {

                "accountId":user_mail_account.account_id,
                "hostname":user_mail_account.account_hostname,
                "engineAddress":user_mail_account.account_host_engine_adress,
                "logInAddress":user_mail_account.account_host_login_adress,

                }
            user_mail_accounts_to_send.append(user_mail_account_to_send)

    return json_resp(user_mail_accounts_to_send)

@api_view(["POST"])
def get_mail_heads(request):

    user=User.objects.filter(username=request.data["userEmail"])
    box_type=request.data["boxType"]
    mail_label=request.data["mailLabel"]
    user_mail_account_id=request.data["userMailAccountId"]

    user_mail_account:UserMailAccounts=UserMailAccounts.objects.get(account_id=user_mail_account_id)

    if mail_label == 'normal':
        if box_type == 'Unread' or box_type == 'Inbox':
            mail_receiver:MailReciever=MailReciever(
                user_mail_account.account_host_engine_adress,
                user_mail_account.account_host_login_adress,
                user_mail_account.account_host_login_password,
                imap_engine_port,
                set_last_mail=int(user_mail_account.account_inbox)
                )
            mail_headers=mail_receiver.fetch_headers()
        else:
            mail_headers=[]
    else:
        mail_headers=[]


    m_headers_to_store=[]
    store_index=0

    if len(mail_headers)>0:
        user_mail_account.account_inbox=mail_headers[0][4]
        user_mail_account.save()
        for _ in mail_headers:
            m_headers_to_store.append(mail_headers[len(mail_headers)-(store_index+1)])
            store_index+=1
    else:
        m_headers_to_store = mail_headers

    mail_heds_to_send=[]
    if len(mail_headers)>0:
        for mail_header in m_headers_to_store:

            mail_subject:str=mail_header[0]
            mail_date:str=mail_header[1]
            mail_from:str=mail_header[2]
            mail_to:str=mail_header[3]
            mail_uid:str=mail_header[4]

            stored_heads=mailHead.objects.filter(
                mail_date=mail_date,subject=mail_subject
            )

            if stored_heads.__len__() == 0:

                m_account=mailAccounts.objects.filter(account_name="INBOX")[0]
                m_object:mailObject=mailObject(
                    system_mail=False,
                    status='Unread',
                    mail_label='normal',
                    mail_server_id=mail_uid,
                    account=m_account,
                    user_account=user_mail_account
                )
                m_object.save()

                m_head:mailHead=mailHead(
                    sender=mail_from,
                    reply_to=mail_from,
                    subject=mail_subject,
                    mail_date=mail_date,
                    mailObject=m_object,
                    recipient=user[0].first_name,
                    recipient_email_address=mail_to
                )
                m_head.save()

                mail_header.append(m_head.mail_head_id)
                mail_header.append(m_object.mail_object_id)
                mail_header.append(m_object.status)
            else:

                for stored_head in stored_heads:
                    mail_header.append(stored_head.mail_head_id)
                    mail_header.append(stored_head.mailObject.mail_object_id)
                    mail_header.append(stored_head.mailObject.status)
                    mail_header.append(stored_head.mailObject.mail_label)
                    mail_header.append(stored_head.mailObject.account.account_name)
                    mail_header.append(stored_head.mailObject.archived)


            mail_heds_to_send.append(mail_header)
    else:

        if mail_label == 'normal':
            if box_type != 'Inbox' and box_type != 'Outbox':
                m_heads=mailHead.objects.filter(mailObject__status=box_type,mailObject__mail_label=mail_label,mailObject__user_account__account_id=user_mail_account_id)[:50]
            else:
                m_heads=mailHead.objects.filter(mailObject__account__account_name=box_type.upper(),mailObject__mail_label=mail_label,mailObject__user_account__account_id=user_mail_account_id)[:50]

        elif mail_label == 'Archive':
            m_heads=mailHead.objects.filter(mailObject__archived=True,mailObject__user_account__account_id=user_mail_account_id)[:50]
        else:
            m_heads=mailHead.objects.filter(mailObject__mail_label=mail_label,mailObject__user_account__account_id=user_mail_account_id)[:50]

        for m_head_obj in m_heads:
            obj_str_id=str(m_head_obj.mailObject.mail_object_id)
            m_head_detail=[
                m_head_obj.subject,m_head_obj.mail_date,
                m_head_obj.sender,m_head_obj.recipient_email_address,
                m_head_obj.mailObject.mail_server_id,m_head_obj.mail_head_id,
                obj_str_id,m_head_obj.mailObject.status,m_head_obj.mailObject.mail_label,
                m_head_obj.mailObject.account.account_name,m_head_obj.mailObject.archived
                ]
            mail_heds_to_send.append(m_head_detail)

    m_headers_to_send=[]
    send_index=0
    if len(mail_heds_to_send)>1:
        for _ in mail_heds_to_send:
            m_headers_to_send.append(mail_heds_to_send[len(mail_heds_to_send)-(send_index+1)])
            send_index+=1
    else:
        m_headers_to_send = mail_heds_to_send

    mail_response=json_resp([0,m_headers_to_send,user[0].username])

    return mail_response

@api_view(["POST"])
def get_mail(request):

    mail_id:str=request.data["mailId"]
    objectId:str=request.data["objectId"]
    user_mail_account_id=request.data["userMailAccountId"]

    user_mail_account:UserMailAccounts=UserMailAccounts.objects.get(account_id=user_mail_account_id)

    m_f_obj=mailObject.objects.get(mail_object_id=objectId)
    m_f_head=mailHead.objects.get(mailObject__mail_object_id=objectId)
    attachments:list=[]

    if m_f_obj.body == False:

        mail_receiver:MailReciever=MailReciever(
            user_mail_account.account_host_engine_adress,
            user_mail_account.account_host_login_adress,
            user_mail_account.account_host_login_password,
            imap_engine_port)
        mail_body=mail_receiver.fetch_body(mail_index=mail_id,folderName=objectId)
        m_f_obj.status='Read'
        m_f_obj.save()
    else:

        m_f_body=mailBody.objects.get(mailObject__mail_object_id=objectId)

        with open (m_f_body.body_url, "r+", encoding="utf-8") as bodyFile:

            file_data=bodyFile.read()

        if m_f_head.att_present == True:

            m_f_atts=mailAttachments.objects.filter(mailHead__mailObject__mail_object_id=objectId)

            for m_f_att in m_f_atts:

                pathList = m_f_att.file_url.split(os.sep)
                media_path="/"+pathList[len(pathList)-4].lower()+"/"+pathList[len(pathList)-3]+"/"+pathList[len(pathList)-2]+"/"+pathList[len(pathList)-1]
                attachments.append(media_path)
        if m_f_obj.account.account_name == "INBOX":
            m_f_obj.status='Read'
            m_f_obj.save()
        mail_response=json_resp([0,'fetched body',file_data,m_f_obj.mail_type,attachments])
        return mail_response


    if mail_body["Attachments_present"]== True:

        m_f_head.att_present=mail_body["Attachments_present"]

        for attachment_folder in mail_body["Attachments_folder"]:

            m_att=mailAttachments(
                file_url=attachment_folder,
                mailHead=m_f_head
            )
            m_att.save()

            pathList = attachment_folder.split(os.sep)
            media_path="/"+pathList[len(pathList)-4].lower()+"/"+pathList[len(pathList)-3]+"/"+pathList[len(pathList)-2]+"/"+pathList[len(pathList)-1]
            attachments.append(media_path)

    m_f_obj.mail_type=mail_body["type"]

    m_f_obj.body=True

    m_f_obj.save()
    m_f_head.save()

    m_body=mailBody(
        mailHead=m_f_head,
        mailObject=m_f_obj
    )

    if mail_body["html_present"] ==True:

        m_body.body_url=mail_body["html_file_location"]

        with open (mail_body["html_file_location"], "r+", encoding="utf-8") as htmlFile:

            file_data=htmlFile.read()

            m_body.save()

            mail_response=json_resp([0,'fetched body',file_data,mail_body["type"],attachments])
            return mail_response
    else:

        m_body.body_url=mail_body["text_file_location"]

        with open (mail_body["text_file_location"], "r+", encoding="utf-8") as htmlFile:

            file_data=htmlFile.read()

            m_body.save()

            mail_response=json_resp([0,'fetched body',file_data,mail_body["type"],attachments])
            return mail_response


@api_view(["POST"])
def uploadFile(request):
    abs_path=handle_uploaded_file(request.FILES['file'])
    mail_response=json_resp([0,abs_path])
    return mail_response


@api_view(["POST"])
def send_mail(request):
    request_data=request.data

    recipient=request_data["recipient"]
    subject=request_data["subject"]
    content=request_data["content"]
    mail_op_type=request_data["mailOpType"]
    mail_action=request_data["mailAction"]
    mail_head_id=request_data["mailHeadId"]
    mail_att=json.loads(request_data["attachments"])
    mail_cc=json.loads(request_data["cc"])
    mail_bcc=json.loads(request_data["bcc"])

    paras=content.split('\n')

    html_text_details={"paras":paras}
    user_mail_account_id=request.data["userMailAccountId"]

    user_mail_account:UserMailAccounts=UserMailAccounts.objects.get(account_id=user_mail_account_id)

    mail_sender=MailSender(
        user_mail_account.account_host_engine_adress,
        smtp_engine_port,
        user_mail_account.account_host_login_adress,
        user_mail_account.account_host_login_password)
    html_text=mail_sender.text_generator(html_text_details)

    m_account=mailAccounts.objects.filter(account_name="OUTBOX")[0]

    user=User.objects.filter(username=request.data["userEmail"])

    m_objs=mailObject.objects.filter(account__account_name="OUTBOX").order_by('-mail_server_id')[:5]

    if(len(m_objs)>0):
        last_mail=int(m_objs[0].mail_server_id)
        last_mail+=1
    else:
        last_mail=0
    if mail_op_type== 'new':
        m_object:mailObject=mailObject(
            system_mail=True,
            status='Draft',
            mail_server_id=last_mail,
            body=True,
            mail_type="multipart",
            mail_label='normal',
            account=m_account,
            user_account=user_mail_account
        )
        m_object.save()
        user_mail_account.account_outbox=last_mail
        user_mail_account.save()
    else:
         m_object:mailObject=mailHead.objects.get(mail_head_id=mail_head_id).mailObject

    details_to_send={
        "reciepient":recipient,
        "subject":subject,
        "content":content,
        "body":html_text,
        "files_details":mail_att,
        "objId":m_object.mail_object_id,
        "body_draft":content,
        "mail_action":mail_action,
        "cc":mail_cc,
        "bcc":mail_bcc
    }

    msg_body_items=mail_sender.send_mail(details_to_send)

    if mail_op_type=='new':
        m_head:mailHead=mailHead(
            sender=user_mail_account.account_host_login_adress,
            reply_to=user_mail_account.account_host_login_adress,
            subject=subject,
            mail_date=timezone.now(),
            mailObject=m_object,
            recipient=recipient,
            recipient_email_address=recipient
        )
        m_head.save()
        mail_head_id=m_head.mail_head_id
    else:
        m_head:mailHead=mailHead.objects.get(mail_head_id=mail_head_id)
        m_head.subject=subject
        m_head.recipient=recipient
        m_head.recipient_email_address=recipient
        m_head.save()
        mail_head_id=m_head.mail_head_id

    if mail_op_type=='new':
        m_body=mailBody(
            mailHead=m_head,
            mailObject=m_object,
            body_url=msg_body_items["text_file_location"],
            body_draft_url=msg_body_items["draft_text_file_location"]
        )
    else:
        m_body=mailBody.objects.get(mailHead__mail_head_id=mail_head_id)
        m_body.body_url=msg_body_items["text_file_location"]
        m_body.body_draft_url=msg_body_items["draft_text_file_location"]

    if msg_body_items["msg_sent"]==True:
        m_object.status="Sent"
        m_object.save()

    m_body.save()
    if msg_body_items["Attachments_present"]== True:

        m_head.att_present=msg_body_items["Attachments_present"]

        for attachment_folder in msg_body_items["Attachments_folder"]:
            p_m_atts=mailAttachments.objects.filter(mailHead__mail_head_id=mail_head_id)
            if len(p_m_atts)>0:
                for p_m_att in p_m_atts:
                    if p_m_att.file_url != attachment_folder:
                        m_att=mailAttachments(
                            file_url=attachment_folder,
                            mailHead=m_head
                        )
                        m_att.save()
            else:
                m_att=mailAttachments(
                    file_url=attachment_folder,
                    mailHead=m_head
                )
                m_att.save()

        m_head.att_present=True
        m_head.save()
    if mail_action == 'send':
        if msg_body_items["msg_sent"]==True:
            mail_response=json_resp([0,'Mail sent'])
        else:
            mail_response=json_resp([1,'Mail not sent but saved as draft'])
    elif mail_action == 'save':
            mail_response=json_resp([2,'Mail saved as draft'])

    return mail_response


@api_view(["Get"])

def get_att(request):

    file_path=request.GET.get('fname','')[1:]
    file_name=file_path.split(os.sep)[len(file_path.split(os.sep))-1]
    att_file_data=None

    with open(file_path,"rb") as att_file:

        att_file_data=att_file.read()

    response = HttpResponse(att_file_data, headers={
        "Access-Control-Allow-Origin":"*",
        "Author":"adedefranklyne@gmail.com",
        "respType":"file",
        'Content-Type': 'application/*',
        "fileName":file_name,
        'Content-Disposition': f'attachment; filename={file_name}',
        'Access-Control-Expose-Headers':"respType,fileName"
     })
    
    return response

@api_view(["POST"])

def get_editable_mail_body(request):
    
    mail_head_id = request.data["mailHeadId"]
    
    mail_body=mailBody.objects.get(mailHead__mail_head_id=int(mail_head_id))
    
    draft_link=mail_body.body_draft_url
    
    mail_atts=mailAttachments.objects.filter(mailHead__mail_head_id=int(mail_head_id))
    mail_atts_to_send=[]
    
    if len(mail_atts)>0:
        
        for mail_att in mail_atts:
            
            pathList = mail_att.file_url.split(os.sep)
            media_path="/"+pathList[len(pathList)-4].lower()+"/"+pathList[len(pathList)-3]+"/"+pathList[len(pathList)-2]+"/"+pathList[len(pathList)-1]
            mail_atts_to_send.append(media_path)
        
    with open (draft_link, "r") as htmlFile:
        
        file_data=htmlFile.read()
        
        mail_response=json_resp([0,'fetched body',file_data,mail_atts_to_send])
        return mail_response

@api_view(["POST"])
def archiveMail(request):
    
    m_obj_id=request.data["mailObjectId"]
    m_object=mailObject.objects.get(mail_object_id=int(m_obj_id))
    m_object.archived=True
    m_object.save()
    mail_response=json_resp([0,'mail Archived'])
    return mail_response

@api_view(["POST"])
def unArchiveMail(request):
    
    m_obj_id=request.data["mailObjectId"]
    m_object=mailObject.objects.get(mail_object_id=int(m_obj_id))
    m_object.archived=False
    m_object.save()
    mail_response=json_resp([0,'Mail removed from archives'])
    return mail_response

@api_view(["POST"])
def trashMail(request):
    
    m_obj_id=request.data["mailObjectId"]
    m_object=mailObject.objects.get(mail_object_id=int(m_obj_id))
    m_object.mail_label='Trash'
    m_object.save()
    mail_response=json_resp([0,'mail trashed'])
    return mail_response

@api_view(["POST"])
def spamMail(request):
    
    m_obj_id=request.data["mailObjectId"]
    m_object=mailObject.objects.get(mail_object_id=int(m_obj_id))
    m_object.mail_label='Spam'
    m_object.save()
    mail_response=json_resp([0,'mail trashed'])
    return mail_response

@api_view(["POST"])
def unTrashMail(request):
    
    m_obj_id=request.data["mailObjectId"]
    m_object=mailObject.objects.get(mail_object_id=int(m_obj_id))
    m_object.mail_label='normal'
    m_object.save()
    mail_response=json_resp([0,'mail trashed'])
    return mail_response

@api_view(["POST"])
def unSpamMail(request):
    
    m_obj_id=request.data["mailObjectId"]
    m_object=mailObject.objects.get(mail_object_id=int(m_obj_id))
    m_object.mail_label='normal'
    m_object.save()
    mail_response=json_resp([0,'mail trashed'])
    return mail_response

@api_view(["POST"])
def clear_box(request):
    
    clear_command =request.data["commandType"]
    
    if clear_command.lower() == 'clear trash':
        mailObject.objects.filter(mail_label='Trash').delete()
        resp_txt = 'Cleared Trash'
        
    elif clear_command.lower() == 'clear spam':
        mailObject.objects.filter(mail_label='Spam').delete()
        resp_txt = 'Cleared Spam'
           
    elif clear_command.lower() == 'clear archive':
        mailObject.objects.filter(archived=True).delete()
        resp_txt = 'Cleared Archives'
        
    mail_response=json_resp([0,resp_txt])
    return mail_response