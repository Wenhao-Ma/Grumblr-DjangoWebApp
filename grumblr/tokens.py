# from itsdangerous import URLSafeTimedSerializer as utsr
# from django.conf import settings as django_settings
#
#
# class Token:
#     def __init__(self, security_key):
#         self.security_key = security_key
#
#     def generate_validate_token(self, username):
#         serializer = utsr(self.security_key)
#         return serializer.dumps({'username': username})
#
#     def confirm_validate_token(self, token, expiration=3600):
#         serializer = utsr(self.security_key)
#         return serializer.loads(token, max_age=expiration)
#
#     def remove_validate_token(self, token):
#         serializer = utsr(self.security_key)
#         return serializer.loads(token)
#
#
# token_confirm = Token(django_settings.SECRET_KEY)
