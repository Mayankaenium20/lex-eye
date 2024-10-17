from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from .serializers import RegisterSerializer

from django.utils import timezone

from random import randint
import re

# Create your views here.


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # print(f"Request data: {request.data}")

        serializer = RegisterSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user = user)
            
            subject = "Registeration Confirmation"
            msg = f"{user.username}. Thank you for registering with LEXEYE!"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            send_mail(
                subject,
                msg,
                from_email,
                recipient_list,
                fail_silently=False,  # This ensures an error is raised if email fails
            )


            return Response({
                "token" : token.key, 
                "message" : "User Registered successfully!"
            }, status = status.HTTP_201_CREATED)

        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username = username, password=password)

        if user is not None:
            # print(f"\n\nTHE USER IS NOT NONE!\n\n")
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                "token": token.key,
                "message": "Login successful",
                "email": user.email,
                "username": user.username,
            }, status=status.HTTP_200_OK)

        # else:
        #     # print(f"\n\nTHE USER IS NOT NONE!\n\n")
        #     # print(f"\n\npassword: {password} username: {username}\n\n")
        

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = Token.objects.get(user = request.user)
            token.delete()
            return Response({"message" : "Successfully logged out!"})
        
        except Token.DoesNotExist:
            return Response({'error' : "Token does not exist!"})
        

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier =request.data.get("identifier")       #email/username
        
        user = None
        if identifier:
            user = User.objects.filter(email = identifier).first() or User.objects.filter(username = identifier).first()

        if user is None:
            return Response({"error" : "Both email and username does not exist! Please register yourself first."})


        otp = randint(100000, 9999999)
        request.session['otp'] = otp
        request.session['user_id'] = user.id
        request.session['otp_timestamp'] = timezone.now().timestamp()                       #stores the current timestamp

        subject = "Password Reset OTP"
        msg = f"Your OTP for password reset is: {otp}."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        try:
            send_mail(subject, msg, from_email, recipient_list, fail_silently=False)

        except Exception as e:
            return Response({'error' : 'Failed to generate an OTP.'})

        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_otp = request.data.get('otp')
        session_otp = request.session.get('otp')
        otp_timestamp = request.session.get('otp_timestamp')

        if user_otp is None or session_otp is None:
            return Response({'error' : "OTP is required!"}, status = status.HTTP_400_BAD_REQUEST)

        if str(user_otp) != str(session_otp):
            return Response({'msg' : 'Invalid OTP'})
        
        if otp_timestamp and (timezone.now().timestamp() - otp_timestamp > 120): 
            return Response({'msg' : "OTP EXPIRED! PLEASE REQUEST A NEW OTP."}, status = status.HTTP_400_BAD_REQUEST)
        
        return Response({"msg" : "OTP verified successfully! Reset your password."}, status = status.HTTP_200_OK)

    

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        user_id = request.session.get('user_id')


        if not user_id:
            return Response({"error" : 'User not found.'}, status = status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"error" : 'Passwords do not match.'}, status = status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            return Response({'error': "Password must be at least 8 characters long."}, status=status.HTTP_400_BAD_REQUEST)

        if not (re.search(r'[A-Za-z]', new_password) and re.search(r'\d', new_password)):
            return Response({'error': "Password must contain at least one letter and one number."}, status=status.HTTP_400_BAD_REQUEST)

                

        try:
            user = User.objects.get(id = user_id)
            user.set_password(new_password)
            user.save()

            del request.session['otp']
            del request.session['user_id']


            return Response({'message': 'Password has been updated successfully.'})

        except User.DoesNotExist:
            return Response({'error' : "user not found!"}, status = status.HTTP_404_NOT_FOUND)