from requests.structures import CaseInsensitiveDict
from dotenv import load_dotenv
import requests
import base64
import msal
import os


class Outlook:
    """
    Esta librería contendrá las funciones que podamos usar de Microsoft Graph
    """

    user_id = None

    def __init__(self):
        """
        Contructor
        """
        load_dotenv()
        

    def login(self, client_id, client_secret, tenant_id):
        """
        Autenticación en la AD Application de Microsoft Graph
        """
        try:
            authority = f"https://login.microsoftonline.com/{tenant_id}"

            app = msal.ConfidentialClientApplication(
                client_id=client_id,
                client_credential=client_secret,
                authority=authority)

            scopes = ["https://graph.microsoft.com/.default"]

            result = app.acquire_token_silent(scopes, account=None)

            if not result:
                print("No suitable token exists in cache. Let's get a new one from Azure Active Directory.")
                result = app.acquire_token_for_client(scopes=scopes)

            if "access_token" in result:
                self._access_ = result["access_token"]
            else:
                self._access_ = None
        except Exception as ex:
            print(f'Excepción al realizar la autenticación: {ex}')

    def send_mail(self, client_id, client_secret, tenant_id, from_mail, to, subject, body, attachment=None, cc=None, bcc=None, replayto=None):
        """
        Envío de correo electrónico
        :param to: A quién envía correo electrónico 1 string, n list
        :param subject: El asunto/titulo del correo electrónico
        :param body: El cuarpo del correo electrónico
        :param attachment: Ruta del archivo a enviar como anexo 1 string, n list
        :param cc: A quién envía correo electrónico de copia 1 string, n list
        :param bcc: A quién envía correo electrónico de copia oculta 1 string, n list
        :param replayto: A quién responde el correo electrónico 1 string, n list
        :param from_mail: Desde donde envía el correo electrónico
        :return:
        """
        try:
            self.login(client_id, client_secret, tenant_id)
            email_message = {
                "message": {
                    "subject": f"{subject}",
                    "body": {
                        "contentType": "HTML",
                        "content": f"{body}"
                    }
                }
            }

            attachments = list()
            toRecipients = list()
            ccRecipients = list()
            bccRecipients = list()
            replyToRecipients = list()

            if to:
                if isinstance(to, str):
                    if to.__contains__(';'):
                        to = to.split(';')
                    elif to.__contains__(','):
                        to = to.split(',')
                    else:
                        to = [to]
                for t in to:
                    toRecipients.append({"emailAddress": {"address": f"{t}"}})
                email_message["message"]['toRecipients'] = toRecipients
            if cc:
                if isinstance(cc, str):
                    if cc.__contains__(';'):
                        cc = cc.split(';')
                    elif cc.__contains__(','):
                        cc = cc.split(',')
                    else:
                        cc = [cc]
                for c in cc:
                    ccRecipients.append({"emailAddress": {"address": f"{c}"}})
                email_message["message"]['ccRecipients'] = ccRecipients
            if bcc:
                if isinstance(bcc, str):
                    if bcc.__contains__(';'):
                        bcc = bcc.split(';')
                    elif bcc.__contains__(','):
                        bcc = bcc.split(',')
                    else:
                        bcc = [bcc]
                for d in bcc:
                    bccRecipients.append({"emailAddress": {"address": f"{d}"}})
                email_message["message"]['bccRecipients'] = bccRecipients
            if replayto:
                if isinstance(replayto, str):
                    if replayto.__contains__(';'):
                        replayto = replayto.split(';')
                    elif replayto.__contains__(','):
                        replayto = replayto.split(',')
                    else:
                        replayto = [replayto]
                for r in replayto:
                    replyToRecipients.append({"emailAddress": {"address": f"{r}"}})
                email_message["message"]['replyTo'] = replyToRecipients
            if attachment:
                if isinstance(attachment, str):
                    if attachment.__contains__(';'):
                        attachment = attachment.split(';')
                    elif attachment.__contains__(','):
                        attachment = attachment.split(',')
                    else:
                        attachment = [attachment]
                for a in attachment:
                    basename = os.path.basename(a)
                    with open(a, "rb") as mg_file:
                        encoded_string = base64.b64encode(mg_file.read())
                        attachments.append({
                            "@odata.type": "#microsoft.graph.fileAttachment",
                            "name": f"{basename}",
                            "contentBytes": encoded_string.decode()
                        })
                email_message["message"]['attachments'] = attachments

            headers = CaseInsensitiveDict()
            headers['Content-type'] = 'application/json'
            headers['authorization'] = f'Bearer {self._access_}'

            endpoint = f'https://graph.microsoft.com/v1.0/users/{from_mail}/sendMail'
            res = requests.post(
                endpoint,
                json=email_message,
                headers=headers,
                timeout=10
            )

            if res.ok:
                print('Sent email successfully')
            else:
                print(res)
        except Exception as ex:
            print('Excepción al envío de correo: {ex}')

    def send_meeting(self, client_id, client_secret, tenant_id, from_mail, attendee, subject, starts, ends, place, body):
        try:
            self.login(client_id, client_secret, tenant_id)
            attendees = list()

            if attendee:
                if isinstance(attendee, str):
                    attendee = [attendee]
                for a in attendee:
                    attendees.append({"emailAddress": {"address": f"{a}"}})

            session_details = {
                'subject': subject,
                'start': {
                    'dateTime': starts,
                    'timeZone': 'America/Mexico_City'
                },
                'end': {
                    'dateTime': ends,
                    'timeZone': 'America/Mexico_City'
                },
                'location': {
                    'displayName': place
                },
                'attendees': attendees,
                'body': {
                    'contentType': 'HTML',
                    'content': body
                },

            }

            headers = CaseInsensitiveDict()
            headers['Content-type'] = 'application/json'
            headers['authorization'] = f'Bearer {self._access_}'

            endpoint = f'https://graph.microsoft.com/v1.0/users/{from_mail}/sendMail'
            res = requests.post(
                endpoint,
                json=session_details,
                headers=headers,
                timeout=10
            )

            if res.ok:
                print('Sent email successfully')
            else:
                print(res)

        except Exception as ex:
            print(f'Excepción al envío de eventos: {ex}')