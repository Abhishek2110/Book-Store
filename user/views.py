from rest_framework.views import APIView
from rest_framework import viewsets
from .serializers import RegisterSerializer, LoginSerializer, EmailSerializer, PasswordSerializer
from rest_framework.response import Response
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.reverse import reverse
import jwt
from .models import User
from jwt import PyJWTError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .tasks import celery_send_mail
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='bookstore.log')

logger = logging.getLogger(__name__)

class RegisterApi(APIView):
    
    throttle_scope = "user_register"
    
    """
    This resource handles the registration of users.

    Methods:
        - POST: Register a New User.

    Request Body:
        - name: str, required. The details of the user to register(username, password, email).

    Responses:
        - 201: If the user is successfully registered. Returns a success message, status code 201, and the registered user data.
        - 400: If there is an error during user registration. Returns an error message and status code 400.
    """
      
    @swagger_auto_schema(request_body=RegisterSerializer, responses={201: openapi.Response(description="User registered", examples={
                             "application/json": {'message': 'User registered', 'status': 201, 'data': {}}
                         }),
                                    400: "Bad Request"})
    # Create your views here.
    def post(self, request):
        try:
            username = request.data['username']
            email = request.data['email']
            if User.objects.filter(username=username).exists():
                return Response({'message': 'Username already exists! Try using a different username', 'status': 400}, status=400)
            if User.objects.filter(email=email).exists():
                return Response({'message': 'Email already exists', 'status': 400}, status=400)
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            token = RefreshToken.for_user(serializer.instance).access_token
            url = f'{settings.BASE_URL}{reverse("register")}?token={token}'
            subject = 'Verification mail Book Store'
            message = f"""Dear {request.data["username"]},\n\nWelcome to Book Store! We're excited to have you as part of our community. \n\nTo begin, please verify your email address by clicking the following link:\n\nVerification Link: {url}\n\nVerifying your email ensures the security of your account and helps us maintain a safe community. If you did not sign up for a Book Store account, please disregard this email.\n\nThank you for choosing Book Store! If you have any questions or require assistance, don't hesitate to contact our support team at abhishekrajpal819@gmail.com.\n\nBest regards,\n\nBook Store Team"""
            from_mail = settings.EMAIL_HOST_USER
            recipient_list = [email]
            celery_send_mail.delay(subject, message, from_mail, recipient_list)
            return Response({'message': 'User registered', 'status': 201, 
                                'data': serializer.data}, status=201)
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)
       
    """
    This resource handles the verification of users.

    Methods:
        - GET: Verifies a New User.

    Request Body:
        - name: str, required. The unique token to verify the user.

    Responses:
        - 200: If the user is successfully verified. Returns a success message, status code 200.
        - 400: If there is an error during user verification. Returns an error message and status code 400.
    """
     
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('token', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)
    ], responses={200: openapi.Response(description="User verified successfully", examples={
                             "application/json": {'message': 'User verified successfully', 'status': 200}
                         }),
                                    400: "Bad Request"})  
    
    def get(self, request):
        try:
            token = request.query_params.get('token')
            if not token:
                return Response({'message': 'Invalid Token', 'status': 400}, status=400)
            payload = jwt.decode(token, key=settings.SIMPLE_JWT.get('SIGNING_KEY'), algorithms=[settings.SIMPLE_JWT.get('ALGORITHM')])
            user = User.objects.get(id=payload['user_id'])
            user.is_verified = True
            user.save()
            return Response({'message': 'User verified successfully', 'status': 200}, status=200)
        except PyJWTError:
            logger.error(f"Invalid token: {str(e)}")
            return Response({'message': 'Invalid token', 'status': 400}, status=400)
        except User.DoesNotExist:
            logger.error(f"User does not exist: {str(e)}") 
            return Response({'message': 'User does not exitst', 'status': 400}, status=400)
        
class LoginApi(APIView):
    
    throttle_scope = "user_login"

    """
    This resource handles the login of users.

    Methods:
        - POST: Login of User.

    Request Body:
        - name: str, required. The details of the user to login(username, password).

    Responses:
        - 200: If the user is successfully logged in. Returns a success message, status code 200, and the unique token.
        - 400: If there is an error during user login. Returns an error message and status code 400.
    """
    
    @swagger_auto_schema(request_body=LoginSerializer, 
                         responses={200: openapi.Response(description="Login successful", examples={
                             "application/json": {'message': 'Login successful', 'status': 200}
                         }),
                                    400: "Bad Request"})
    
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            token = RefreshToken.for_user(serializer.instance).access_token
            return Response({'message': 'Login successful', 'status': 200, 'token': str(token)}, status=200)
        # User authentication failed
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)

class ResetPasswordApi(viewsets.ViewSet):
    
    throttle_scope = "reset_password"
    
    """
    This resource handles the reset password send mail.

    Methods:
        - POST: Sends email for reset password.

    Request Body:
        - name: str, required. The email of the user to send reset password link.

    Responses:
        - 200: If the email is sent. Returns a success message, status code 200, and the unique token.
        - 400: If there is an error during send mail. Returns an error message and status code 400.
        - 404: If mail not found. Returns an error message email not found and status code 404.
    """
    
    @swagger_auto_schema(request_body=EmailSerializer, 
                         responses={200: openapi.Response(description="Email Sent Successfully", examples={
                             "application/json": {'message': 'An Email is sent', 'status': 200}
                         }),
                                    400: "Bad Request"})
    
    def send_reset_password_link(self, request):
        try:
            email = request.data['email']
            mail = User.objects.filter(email = email).first()
            if(mail):
                token = RefreshToken.for_user(mail).access_token
                url = f'{settings.BASE_URL}{reverse("reset")}?token={token}'
                subject = 'Reset Password Link'
                message = f"""Hi ,This is your reset password link:\n\nPassword Reset Link: {url}"""
                from_mail = settings.EMAIL_HOST_USER
                recipient_list = [email]
                celery_send_mail.delay(subject, message, from_mail, recipient_list)
                return Response({'message': 'An Email is sent', 'status': 200, 'token': str(token)}, status=200)
            return Response({'message': 'Email not found', 'status': 404}, status=404)
        except Exception as e:
            logger.error(f"Some error occured while sending mail: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)
        
    """
    This resource handles the change password.

    Methods:
        - POST: Sends new password.

    Request Body:
        - name: str, required. The new password of the user to reset password.

    Responses:
        - 200: If the Password Updated Successfully. Returns a success message, status code 200.
        - 400: If there is an password updation. Returns an error message and status code 400.
    """
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('token', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)],request_body=PasswordSerializer, 
                         responses={200: openapi.Response(description="Password Updated", examples={
                             "application/json": {'message': 'Password Updated Successfully', 'status': 200}
                         }),
                                    400: "Bad Request"})
     
    def change_password(self, request):
        try:
            token = request.query_params.get('token')
            if not token:
                return Response({'message': 'Invalid Token', 'status': 400}, status=400)
            payload = jwt.decode(token, key=settings.SIMPLE_JWT.get('SIGNING_KEY'), algorithms=[settings.SIMPLE_JWT.get('ALGORITHM')])
            new_password = request.data["new_password"]
            user = User.objects.get(id=payload['user_id'])
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password Updated Successfully', 'status': 200}, status=200)
        except Exception as e:
            logger.error(f"Some error occured while changing the password: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)