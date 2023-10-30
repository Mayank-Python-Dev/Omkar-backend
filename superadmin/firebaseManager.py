import firebase_admin,os
from firebase_admin import credentials,messaging
GoogleCredentialsPath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'firebase/omkar_development.json')
cred = credentials.Certificate(GoogleCredentialsPath)
firebase_admin.initialize_app(cred)

# token = ["eDDMYLfqQxi87eoLdLicOC:APA91bHIYRLj9xvJa7SpqBnYa9Pac9VMnikkO1MB4vvrLRmylClasnq8vV-TK9g-22xTF1n9ouYHQz_Ho2Bgn0gxY0LLa_Ad6ofk3iKfxVWuI7qDrVcy1bxVSX7MVA8a3F81gEP0DIhx"]
def sendPush(title,msg,registration_token,dataObject=None):
    message = messaging.MulticastMessage(
        notification = messaging.Notification(
            title = title,
            body = msg,
        ),
        data = dataObject,
        tokens = registration_token
    )
    response = messaging.send_multicast(message)
    # print(response.__dir__())
    # print(response.success_count)
    # print(response.failure_count)
# sendPush("Testing","Hello,World!",token)