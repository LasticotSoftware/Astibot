#from twilio.rest import Client
import TradingBotConfig as theConfig

def SendWhatsappMessage(messageToSend):
    if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
        pass
        # Your Account Sid and Auth Token from twilio.com/console
#         account_sid = '<fill id here>'
#         auth_token = '<fill id here>'
#         client = Client(account_sid, auth_token)
#         
#         
#         message = client.messages.create(
#                                       body=messageToSend,
#                                       from_='whatsapp:+<fill number here>',
#                                       to='whatsapp:+<fill number here>'
#                                   )
#              
#         print("NOTI - Sent message, %s" % message)
        