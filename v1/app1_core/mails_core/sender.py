from email.message import EmailMessage
import smtplib
import os

class MailSender():
    def __init__(self, engine_address,engine_port,user_name,password):
        self.engine_address=engine_address
        self.engine_port=engine_port
        self.user_name=user_name
        self.password=password
    
    def clean(self,text):
        # clean text for creating a folder
        return "".join(c if c.isalnum() else "_" for c in str(text))
       
    def text_generator(self,mail_variables):
        text_paras="<div>"
        
        for para in mail_variables["paras"]:
            text_para=f"<p>{para}</p>"
            text_paras+=text_para
            
        text_paras+="</div>"
        
        html_text=f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Vincowoods</title>
            </head>
            <body>
                <div class="holder">
                    <div class="mainbody">
                        {text_paras}
                    </div>
                    <div class="vwMailFooterDetails">
                        <h3>
                            Kind Regards,
                        </h3>
                        <table>
                            <tr>
                                <td>
                                    <div class="vWMFDImgHolder"">
                                        <img src="https://www.vincowoods.com/static/static_images/VWLogo.png" class="vWMFDImgTag"
                                        style="width: 110px;">
                                        <div style="width: 110px; font-size:10px;color:blue;font-weight:700">
                                            <div style="position: relative;left:10px;">
                                                VINCO W LIMITED
                                            </div>
                                            <div style="position: relative;left:15px;">
                                                VINCO WOODS
                                            </div>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <div class="vWMFDCompanyDetails">
                                        <h3 class="vwOwnername">        
                                            Vincent J Agutu | Director | Kenya 
                                        </h3>
                                        <p style="color: gray;">
                                            MBA (USW,United Kingdom), BSc (UoN,Kenya)
                                        </p>
                                        <div class="vWOwnermobiles">
                                            <h4 class="vWOMTitle">
                                                Mobiles: +254782914632, +254728914632
                                            </h4> 
                                        </div>
                                                
                                        <h4>
                                            Tembo Plaza, Garden Estate Road
                                        </h4>

                                        <h4 class="websitelink">
                                            Website: <a href="https://www.vincowoods.com" target="_blank" rel="noopener noreferrer">www.vincowoods.com</a>
                                        </h4>
                                    </div>
                                </td>
                            </tr>
                        </table>         
                        
                    </div>
                </div>
            </body>
            </html>
        """
        return html_text
    
    def send_mail(self,mail_details):
        EmailMsg=EmailMessage()
        EmailMsg['from']=self.user_name
        EmailMsg['Subject']=mail_details["subject"]
        EmailMsg["cc"]=mail_details["cc"]
        EmailMsg["bcc"]=mail_details["bcc"]

        EmailMsg.set_content(mail_details["content"])
        EmailMsg.add_alternative(mail_details["body"],subtype='html')
        
        msg_body_items={}
        
        folder_name = self.clean(mail_details["objId"])
        folder_name="media/"+folder_name
        
        if not os.path.isdir(folder_name):
            # make a folder for this email (named after the subject)
            os.mkdir(folder_name)
            
        file_name="vw_index.txt"
        file_path = os.path.join(folder_name, file_name)
        
        with open(file_path,"wb") as txt_file:
            txt_file.write(mail_details["body"].encode("utf-8"))
        
        txt_file_path=os.path.join(os.path.abspath(folder_name), file_name)
            
        draft_file_name="draft_vw_index.txt"
        draft_file_path = os.path.join(folder_name, draft_file_name)
        
        with open(draft_file_path,"wb") as txt_file:
            txt_file.write(mail_details["body_draft"].encode("utf-8"))
            
        draft_txt_file_path=os.path.join(os.path.abspath(folder_name), draft_file_name)
        msg_body_items["text_file_location"]=draft_txt_file_path
        msg_body_items["draft_text_file_location"]=draft_txt_file_path
        
        img_file_types=['.JPG','.PNG','.GIF','.WEBP','.TIFF','.PSD','.RAW','.BMP','.HEIF','.INDD','.JPEG','.SVG','.AI','.EPS']
        video_fle_types=['.WEBM','.MPG','.MP2','.MPEG','.MPE','.MPV','.OGG','.MP4','.M4P','.M4V','.AVI','.WMV','.MOV','.QT','.FLV', 
                         '.SWF','.AVCHD']
        
        attachments_location=[]
        msg_body_items["Attachments_present"]=False
        if(len(mail_details["files_details"])>0):
            
            msg_body_items["Attachments_present"]=True
            
            for file_details in mail_details["files_details"]:
                file_type=os.path.splitext(file_details)[1]
                type_found=False
                attached_file_type=None
                
                file_name = file_details.split(os.sep)[len(file_details.split(os.sep))-1]
                attachment_folder_name="attachments"
                folder_path = os.path.join(folder_name, attachment_folder_name)
                
                if not os.path.isdir(folder_path):
                    os.mkdir(folder_path)
                    
                filepath = os.path.join(folder_path, file_name)
                            
                for img_type in img_file_types:
                    if file_type.lower() == img_type.lower():
                        attached_file_type="image"
                        type_found=True
                        
                if type_found==False:                
                    for vid_type in video_fle_types:
                        if file_type.lower() == vid_type.lower():
                            attached_file_type="Video"
                            type_found=True
                            
                if type_found==False:
                    attached_file_type="application"
                
                s_c = file_details[:1]
                
                if s_c != '/m':
                    
                    with open(file_details,"rb") as attachment_file:
                        attachment_file_content=attachment_file.read()                
                        EmailMsg.add_attachment(attachment_file_content, maintype=attached_file_type, subtype=file_type[1:], filename=file_name)
                                           
                        with open(filepath, "wb") as atcmtfile:
                            atcmtfile.write(attachment_file_content)
                            
                        attachments_location.append(os.path.abspath(filepath))
                        
                        os.remove(file_details)
                
                else:
                    
                    with open(file_details[1:],"rb") as attachment_file:
                        attachment_file_content=attachment_file.read()                
                        EmailMsg.add_attachment(attachment_file_content, maintype=attached_file_type, subtype=file_type[1:], filename=file_name)
                                           
                        with open(filepath, "wb") as atcmtfile:
                            atcmtfile.write(attachment_file_content)
                            
                        attachments_location.append(os.path.abspath(filepath))

            msg_body_items["Attachments_folder"]=attachments_location
        
        if mail_details["mail_action"] == 'send':

            for mail_cc in mail_details["bcc"]:

                with smtplib.SMTP_SSL(host=self.engine_address,port=self.engine_port) as smtp:
                    smtp.login(self.user_name,self.password)
                    try:

                        del EmailMsg['to']
                        EmailMsg['to']=mail_cc
                        smtp.send_message(EmailMsg)
                        smtp.close()

                    except:
                        smtp.close()
                        msg_body_items["msg_sent"]=False
                        return None

            for mail_cc in mail_details["cc"]:

                with smtplib.SMTP_SSL(host=self.engine_address,port=self.engine_port) as smtp:
                    smtp.login(self.user_name,self.password)
                    try:
                        del EmailMsg['to']
                        EmailMsg['to']=mail_cc
                        smtp.send_message(EmailMsg)
                        smtp.close()

                    except:
                        smtp.close()
                        msg_body_items["msg_sent"]=False
                        return None
            with smtplib.SMTP_SSL(host=self.engine_address,port=self.engine_port) as smtp:
                smtp.login(self.user_name,self.password)
                try:
                    del EmailMsg['to']
                    EmailMsg['to']=mail_details["reciepient"]
                    smtp.send_message(EmailMsg)
                    smtp.close()
                    msg_body_items["text_file_location"]=txt_file_path
                    msg_body_items["msg_sent"]=True

                    return msg_body_items

                except Exception as ex:
                    smtp.close()
                    msg_body_items["msg_sent"]=False
                    return msg_body_items
        else:
            msg_body_items["msg_sent"]=False
            msg_body_items["text_file_location"]=txt_file_path
            return msg_body_items
            
            
        