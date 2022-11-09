import email
from email.header import decode_header, make_header
import imaplib
import os

class MailReciever:

    # Initializing the Receiving engine with mail engine credantials and user credantials

    def __init__(self,
                 mail_engine_address:str="",
                 login_email_address:str="",
                 login_password:str="",
                 mail_engine_port:int=0,
                 set_max_mails:int=100,
                 set_last_mail:int=0
                 ):

        self.engine_address:str=mail_engine_address
        self.engine_port:str=mail_engine_port
        self.login_address:str=login_email_address
        self.login_password:str=login_password
        self.port_prsent:bool=False if self.engine_port==0 else True
        self.max_mails:int=set_max_mails
        self.last_mail=set_last_mail

    def clean(self,text):
        # clean text for creating a folder
        return "".join(c if c.isalnum() else "_" for c in text)

    def conn_and_auth(self):

        if self.port_prsent:
            try:
                # create an IMAP4 object with SSL if port present
                imap = imaplib.IMAP4_SSL(self.engine_address,993)
            except:
                print("There is a connection problem check if your Engine Address and engine port are correct and also check if your are connected to the internet then try again.")
                exit()
            try:
                # authenticate
                imap.login(self.login_address, self.login_password)
            except:
                print("Log in failed check your credentails and try again.")
                exit()

        else:

            try:
                # create an IMAP4 object with SSL if port present
                imap = imaplib.IMAP4_SSL(self.engine_address,993)
            except:
                print("There is a connection problem check if your Engine Address and engine port are correct and also check if your are connected to the internet then try again.")
                exit()
            try:
                # authenticate
                imap.login(self.login_address, self.login_password)
            except:
                print("Log in failed check your credentails and try again.")
                exit()

        return imap

    def header_list(self,mesg_header,items_to_get:list,header_uid):

        for msg_response in mesg_header:

            if isinstance(msg_response,tuple):
                msg_header_details=email.message_from_bytes(msg_response[1])

                msg_list=[]

                for item_to_get in items_to_get:

                    if msg_header_details[item_to_get] != None:
                        msg_item_gotten,_=decode_header(msg_header_details[item_to_get])[0]
                    else:
                        msg_item_gotten=None

                    if isinstance(msg_item_gotten,bytes):
                        msg_item_gotten_from_bytes=msg_item_gotten.decode()
                        msg_list.append(msg_item_gotten_from_bytes)

                    else:
                        msg_list.append(msg_item_gotten)

                msg_list.append(header_uid)

        return msg_list

    """ Returns a list that contains lists of email headers in the following order ( SUBJECT DATE FROM TO )
        for each email in the chosen box,either INBOX,OUTBOX,SENTBOX,SPAMBOX
    """
    def fetch_headers(self,box_type="INBOX"):

        if box_type.upper()!="INBOX":
            box_type=f"INBOX.{box_type}"

        imap=self.conn_and_auth()
        status, messages = imap.select(box_type)
        self.mails_numb=self.max_mails if int(messages[0])>self.max_mails else int(messages[0])
        mail_list=[]

        for mail_index in range(self.mails_numb, self.last_mail, -1):
            _, msg = imap.fetch(str(mail_index).encode(encoding='utf-8'), "BODY.PEEK[HEADER.FIELDS (SUBJECT DATE FROM TO)]")
            items_to_get=["SUBJECT","DATE","FROM","TO"]
            mail_list.append(self.header_list(msg,items_to_get,mail_index))

        if status=="OK":
            imap.logout()
            return mail_list

        else:
            imap.logout()
            return mail_list
    def get_saved_results_url(self,file_name):
        dirname = os.path.dirname(__file__)
        pathList = dirname.split(os.sep)
        pathList.pop()
        pathList.pop()
        pathList.pop()
        newPath='/'.join(pathList)
        newCompletePath= newPath+'/'+file_name
        return newCompletePath

    def body_list(self,msg_body,folderName):
        attachments_location:list=[]
        for msg_response in msg_body:

            if isinstance(msg_response,tuple):
                msg_body_details=email.message_from_bytes(msg_response[1])
                msg_body_items={}
                msg_body_items["Attachments_present"]=False

                msg_body_items["html_present"] = False

                subject,_ = decode_header(msg_body_details["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode()
                else:
                   subject=subject
                # Check if the email message is multipart
                if msg_body_details.is_multipart():
                    msg_body_items["type"]="multipart"
                    # iterate over email parts
                    for part in msg_body_details.walk():

                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass

                        if content_type == "text/plain" :
                            folder_name = self.clean(folderName)
                            folder_name="media/"+folder_name

                            if not os.path.isdir(folder_name):
                                # make a folder for this email (named after the subject)
                                os.mkdir(folder_name)

                            file_name="vw_index.txt"
                            file_path = os.path.join(folder_name, file_name)

                            with open(file_path,"wb") as txt_file:
                                txt_file.write(body.encode("utf-8"))

                            txt_file_path=os.path.join(os.path.abspath(folder_name), file_name)
                            msg_body_items["text_file_location"]=txt_file_path

                        elif content_type == "text/html":

                            msg_body_items["html_present"] = True

                            folder_name = self.clean(folderName)
                            folder_name="media/"+folder_name

                            if not os.path.isdir(folder_name):
                                # make a folder for this email (named after the subject)
                                os.mkdir(folder_name)

                            file_name = "vw_index.html"
                            file_path = os.path.join(folder_name, file_name)

                            # write the file
                            open(file_path, "w", newline='',encoding="utf-8").write(body)

                            html_file_path=os.path.join(os.path.abspath(folder_name), file_name)
                            msg_body_items["html_file_location"]=html_file_path

                        if "attachment" in content_disposition:

                            # download attachment
                            if os.path.splitext(part.get_filename())[1]=="":
                                filename = 'Unsupported file'
                            else:
                                filename=part.get_filename()

                            folder_name = self.clean(folderName)
                            folder_name="media/"+folder_name

                            if not os.path.isdir(folder_name):
                                # make a folder for this email (named after the subject)
                                os.mkdir(folder_name)

                            attachment_folder_name="attachments"
                            folder_path = os.path.join(folder_name, attachment_folder_name)

                            if not os.path.isdir(folder_path):
                                os.mkdir(folder_path)

                            filepath = os.path.join(folder_path, filename)
                            # download attachment and save it
                            with open(filepath, "wb") as atcmtfile:
                                atcmtfile.write(part.get_payload(decode=True))

                            attachments_location.append(os.path.abspath(filepath))
                            msg_body_items["Attachments_present"]=True

                            msg_body_items["Attachments_folder"]=attachments_location


                else:
                    # extract content type of email
                    content_type = msg_body_details.get_content_type()

                    # get the email body
                    body = msg_body_details.get_payload(decode=True).decode()

                    if content_type == "text/plain":
                        msg_body_items["type"]="singlepart"
                        # Write text/plain emails to text docs

                        folder_name = self.clean(folderName)
                        folder_name="media/"+folder_name

                        if not os.path.isdir(folder_name):
                            # make a folder for this email (named after the subject)
                            os.mkdir(folder_name)

                        file_name = self.clean(subject)+".txt"
                        filepath = os.path.join(folder_name, file_name)

                        with open(filepath,"w") as txt_file:
                            txt_file.write(body)

                        single_part_file_location=os.path.abspath(filepath)

                        msg_body_items["text_file_location"]=single_part_file_location

                    else:
                        # Write text/html emails to text docs
                        msg_body_items["type"]="multipart"

                        folder_name = self.clean(folderName)
                        folder_name="media/"+folder_name

                        if not os.path.isdir(folder_name):
                            # make a folder for this email (named after the subject)
                            os.mkdir(folder_name)

                        file_name = self.clean(subject)+".txt"
                        filepath = os.path.join(folder_name, file_name)

                        with open(filepath,"w") as txt_file:
                            txt_file.write(body)

                        single_part_file_location=os.path.abspath(filepath)

                        msg_body_items["html_file_location"]=single_part_file_location

        return msg_body_items

    def fetch_body(self,box_type="INBOX",mail_index:int=1,folderName:str="default"):

        imap=self.conn_and_auth()
        # print(imap.list())
        status, _ = imap.select(box_type)

        _, msg = imap.fetch(str(mail_index).encode(encoding='utf-8'), "(RFC822)")
        email_items=self.body_list(msg,folderName)

        if status=="OK":
            imap.logout()
            return email_items

        else:
            imap.logout
            return None
