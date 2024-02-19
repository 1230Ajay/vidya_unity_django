from django.core.mail import send_mail
from django.conf import settings

class UserUtils:
    def verify_user_account(self,email, uid):
        try:
            Sub = "Verify your account"
            message = f"Hello from vidya unity, Your account has created successfully! Now you need to verify your account by clicking the following link to verify your account http://127.0.0.1:8000/auth/verify_account/{uid}/"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(Sub, message, email_from, recipient_list)
            print("email is sent to your email")
        
        except Exception as e:
            print(f"somehting went wrong error is : {e}")
            return False