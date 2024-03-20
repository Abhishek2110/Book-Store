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

class RegisterApi(APIView):
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
            return Response({'message': str(e), 'status': 400}, status=400)
        
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
            return Response({'message': 'Invalid token', 'status': 400}, status=400)
        except User.DoesNotExist:
            return Response({'message': 'User does not exitst', 'status': 400}, status=400)
        
class LoginApi(APIView):

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
            return Response({'message': str(e), 'status': 400}, status=400)

class ResetPasswordApi(viewsets.ViewSet):
    
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
                return Response({'message': 'An Email is sent', 'status': 200}, status=200)
            return Response({'message': 'Email not found', 'status': 404}, status=404)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)
        
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
            return Response({'message': str(e), 'status': 400}, status=400)