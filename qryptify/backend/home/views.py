from django.shortcuts import render
import requests
import os
import base64
import re
import binascii 
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from home.models import User, AuditLog
from home.audits import audit_logs
from qryptify.settings import DEFAULT_TO_EMAIL1, DEFAULT_TO_EMAIL2, DEFAULT_TO_EMAIL3
from .serializers import UserSerializer, AuditLogSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.sessions.models import Session 
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from datetime import timedelta
from rest_framework.permissions import AllowAny
from django.utils import timezone  
from .nist_sts import *
from django.contrib.auth import update_session_auth_hash




def get_csrf_token(request):
    print("inside the get_csrf_token")
    return JsonResponse({"token": get_token(request)}) 

class GetLogsAPI(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        logs = AuditLog.objects.all()
        serializer = AuditLogSerializer(logs, many=True)
        return Response({
            "status": True, 
            "log_data": serializer.data
        })
    


class EmailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get("message")

        if not message or not message.strip():
            return Response(
                {"status": False, "message": "Message cannot be empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            send_mail(
                subject="Support Request",
                message=message,
                from_email=request.user.email,
                recipient_list=[
                    DEFAULT_TO_EMAIL1,
                    DEFAULT_TO_EMAIL2,
                    DEFAULT_TO_EMAIL3,
                ],
                fail_silently=False,
            )
        except Exception:
            return Response(
                {"status": False, "message": "Failed to send email"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"status": True, "message": "Mail successfully sent"},
            status=status.HTTP_200_OK
        )


class UpdateUserDetailsAPI(APIView):

    permission_classes=[IsAuthenticated]
    def patch(self,request):
        updated_user_data=request.data
        user=request.user
        serializers=UserSerializer(
            user,
            data=updated_user_data,
            partial=True
        )
        if serializers.is_valid():
            serializers.save()
            audit_logs(
                actor=request.user,
                action='UPDATE',
                message=f"{request.user.username} updated profile details"
            )
            return Response({"status":True,"message":"Profile successfully updated"})
        return Response({"status":False,"message":"Error in updating the profile"})


class ResetPasswordAPI(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user

        current_password = request.data.get("currentPassword")
        new_password = request.data.get("newPassword")
        confirm_password = request.data.get("confirmPassword")

        if not all([current_password, new_password, confirm_password]):
            return Response(
                {"status": False, "message": "All password fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(current_password):
            return Response(
                {"status": False, "message": "Current password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_password != confirm_password:
            return Response(
                {"status": False, "message": "Passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password == current_password:
            print("new password = current password")
            return Response(
                {"status":False,"message":"New password should not match current password"},
                 status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)

        return Response(
            {"status": True, "message": "Password updated successfully"},
            status=status.HTTP_200_OK
        )




# class LoginAPI(APIView):
#     permission_classes = [AllowAny]
    
#     def get(self, request):
#         users_obj = User.objects.all()
#         if not users_obj.exists():
#             return Response({"status": False, "message": "No user exists"}, status=status.HTTP_404_NOT_FOUND)
#         serializers = UserSerializer(users_obj, many=True)
#         return Response({"status": True, "data": serializers.data}, status=status.HTTP_200_OK)

#     def post(self, request):
#         data = request.data
#         email = data.get('email')
#         password = data.get('password')
#         remember_me = data.get('rememberMe', False)

#         if not email or not password:
#             return Response(
#                 {"status": False, "message": "Email and password are required"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({"status": False, "message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
#         user = authenticate(username=user.username, password=password)
#         if not user:
#             return Response({"status": False, "message": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

#         # ← ADD THIS: Update last_login manually for JWT
#         user.last_login = timezone.now()
#         user.save(update_fields=['last_login'])

#         refresh_token = RefreshToken.for_user(user)
#         access_token = str(refresh_token.access_token)
        
#         if remember_me:
#             print("remember me is checked")
#         else:
#             print("remember me is not checked")

#         cookie_max_age = 7 * 24 * 60 * 60 if remember_me else 2*24 * 60 * 60

#         res = Response({
#             "status": True,
#             "message": "Successfully logged in",
#             "access": access_token
#         }, status=status.HTTP_200_OK)
#         res.set_cookie(
#             key='refresh',
#             value=str(refresh_token),
#             httponly=True,
#             secure=False,
#             samesite="Lax",
#             max_age=cookie_max_age
#         )
#         return res

#     def patch(self, request):
#         data = request.data
#         email = data.get('email')

#         try:
#             obj = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({"status": False, "message": "No user exists"}, status=status.HTTP_404_NOT_FOUND)

#         new_password = data.get('newPassword')
#         confirm_password = data.get('confirmPassword')

#         if new_password:
#             if new_password != confirm_password:
#                 return Response({"status": False, "message": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
#             obj.set_password(new_password)
#             obj.save()
#             return Response({"status": True, "message": "Password updated successfully"})

#         serializer = UserSerializer(obj, data=data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"status": True, "message": "Successfully updated"})
#         return Response({"status": False, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request):
#         data = request.data
#         email = data.get('email')
#         user = User.objects.filter(email=email)
#         user.delete()
#         return Response({"status": True, "message": "Successfully deleted"})
    

class LoginAPI(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        users_obj = User.objects.all()
        if not users_obj.exists():
            return Response({"status": False, "message": "No user exists"}, status=status.HTTP_404_NOT_FOUND)
        serializers = UserSerializer(users_obj, many=True)
        return Response({"status": True, "data": serializers.data}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        remember_me = data.get('rememberMe', False)

        if not email or not password:
            return Response(
                {"status": False, "message": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"status": False, "message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        user = authenticate(username=user.username, password=password)
        if not user:
            return Response({"status": False, "message": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Update last_login manually for JWT
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        refresh_token = RefreshToken.for_user(user)
        access_token = str(refresh_token.access_token)
        
        if remember_me:
            print("remember me is checked")
        else:
            print("remember me is not checked")

        # Set cookie ages based on remember_me
        access_cookie_max_age = 7 * 24 * 60 * 60 if remember_me else 2 * 24 * 60 * 60  # 7 days or 2 days
        refresh_cookie_max_age = 30 * 24 * 60 * 60 if remember_me else 7 * 24 * 60 * 60  # 30 days or 7 days

        # Create response
        res = Response({
            "status": True,
            "message": "Successfully logged in",
            "access": access_token  # Still return for backward compatibility
        }, status=status.HTTP_200_OK)
        
        # ✅ ADD ACCESS TOKEN COOKIE (HttpOnly)
        res.set_cookie(
            key='access',
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,  # Secure=True in production, False in dev
            samesite="Lax",
            max_age=access_cookie_max_age,
            path='/'
        )
        
        # ✅ REFRESH TOKEN COOKIE (HttpOnly)
        res.set_cookie(
            key='refresh',
            value=str(refresh_token),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            max_age=refresh_cookie_max_age,
            path='/'
        )

        audit_logs(
                actor=user,
                action='LOGIN',
                message=f"{user.username} logged in"
            )
        
        return res

    def patch(self, request):
        data = request.data
        email = data.get('email')

        try:
            obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"status": False, "message": "No user exists"}, status=status.HTTP_404_NOT_FOUND)

        new_password = data.get('newPassword')
        confirm_password = data.get('confirmPassword')

        if new_password:
            if new_password != confirm_password:
                return Response({"status": False, "message": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
            obj.set_password(new_password)
            obj.save()
            return Response({"status": True, "message": "Password updated successfully"})

        serializer = UserSerializer(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Successfully updated"})
        return Response({"status": False, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        data = request.data
        email = data.get('email')
        user = User.objects.filter(email=email)
        user.delete()
        return Response({"status": True, "message": "Successfully deleted"})
# class DeleteAccountUserAPI(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def delete(self, request):
#         user = request.user
#         try:
#             user.delete()
#             res = Response({"status": True, "message": "Account successfully deleted"})
#             res.delete_cookie('refresh')
#             return res
#         except Exception as e:
#             return Response({"status": False, "message": str(e)}, status=400)

class DeleteAccountUserAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        user = request.user
        try:
            user.delete()
            res = Response({"status": True, "message": "Account successfully deleted"})
            # ✅ Delete BOTH cookies
            res.delete_cookie('access', path='/')
            res.delete_cookie('refresh', path='/')
            audit_logs(
                actor=request.user,
                action='DELETE',
                message=f"{request.user.username} updated profile details"
            )
            return res
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=400)
    
# Add this new view to your views.py
class GetAccessTokenAPI(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get access token from cookies (for frontend backward compatibility)"""
        access_token = request.COOKIES.get('access')
        
        if access_token:
            return Response({
                "status": True,
                "access": access_token
            })
        
        return Response({
            "status": False,
            "message": "No access token found"
        }, status=401)


class SignupAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        serializer = UserSerializer(data=data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = serializer.save()
        print('user details created')
        audit_logs(
                actor=request.user,
                action='CREATE',
                target_user=user,
                message=f"{request.user.username} created {user.username}"
            )
        return Response(
                {"status": True, "message": "User created successfully"},
                status=status.HTTP_201_CREATED
            )


# class LogoutAPI(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         print(request.user)
#         res = Response({"status": True, "message": "Successfully logged out"})
#         res.delete_cookie('refresh')
#         return res

class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        print(request.user)
        res = Response({"status": True, "message": "Successfully logged out"})
        # ✅ Delete BOTH cookies
        res.delete_cookie('access', path='/')
        res.delete_cookie('refresh', path='/')
        audit_logs(
                actor=request.user,
                action='LOGOUT',
                message=f"{request.user.username} logged out"
            )
        return res


class UserDetailsAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        refresh = request.COOKIES.get("refresh")
        if not refresh:
            return Response({"status": False, "message": "Not logged in"}, status=401)

        try:
            refresh_token = RefreshToken(refresh)
            user = User.objects.get(id=refresh_token['user_id'])
            return Response({
                "status": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": user.phone,
                    "role": user.role,
                    "last_login": user.last_login,
                    "date_joined": user.date_joined,  
                    "is_active": user.is_active,
                }
            })
        except Exception:
            return Response({"status": False, "message": "Invalid refresh"}, status=401)


# class RefreshTokenAPI(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request):
#         refresh = request.COOKIES.get('refresh')
#         if not refresh:
#             return Response({"status": False, "message": "Refresh token expired"},
#                             status=status.HTTP_401_UNAUTHORIZED)
#         try:
#             refresh_token = RefreshToken(refresh)
#             new_access = str(refresh_token.access_token) 
#             return Response({"status": True, "access": new_access})
#         except TokenError:
#             return Response({"status": False, "message": "Token error occurred"},
#                             status=status.HTTP_401_UNAUTHORIZED)

class RefreshTokenAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        refresh = request.COOKIES.get('refresh')
        if not refresh:
            return Response({"status": False, "message": "Refresh token expired"},
                            status=status.HTTP_401_UNAUTHORIZED)
        try:
            refresh_token = RefreshToken(refresh)
            new_access = str(refresh_token.access_token)
            
            # ✅ Create response
            res = Response({"status": True, "access": new_access})
            
            # ✅ Update access token cookie
            res.set_cookie(
                key='access',
                value=new_access,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                max_age=2 * 24 * 60 * 60,  # 2 days
                path='/'
            )
            
            return res
        except TokenError:
            return Response({"status": False, "message": "Token error occurred"},
                            status=status.HTTP_401_UNAUTHORIZED)

def is_base64_string(data_bytes):
    try:
        data_string = data_bytes.decode('utf-8').strip()
        if not re.match(r'^[A-Za-z0-9+/=\s]*$', data_string):
            return False
        base64.b64decode(data_string, validate=True)
        return True
        
    except (UnicodeDecodeError, binascii.Error):
        return False
    except Exception:
        return False 

def convert_to_bits(data: str):
    total_length = len(data)
    print(f"   Total rows: {total_length}")
    try:
        cipher_bytes = base64.b64decode(data)
        return ''.join(f'{byte:08b}' for byte in cipher_bytes)
    except Exception:
        return data 

    
class AnalyzeUserInputAPI(APIView):
    ALLOWED_EXTENSIONS = ['.txt', '.dat', '.bin', '.enc', '.pdf', '.docx', '.doc']
    ALLOWED_MIME_TYPES = [
        'text/plain', 
        'application/octet-stream', 
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    def post(self, request):
        uploaded_file = request.FILES.get('file')
        
        if not uploaded_file:
            print("ERROR: File not found in request.FILES. Check FormData key ('file').")
            return Response({"status": False, "message": "No file received"}, status=400)
        
        file_name = uploaded_file.name
        file_size = uploaded_file.size
        name, file_extension = os.path.splitext(file_name)
        file_extension = file_extension.lower() 
        file_mime_type = uploaded_file.content_type
        
        print(f"2. File Metadata Collected: Name='{file_name}', Size={file_size} bytes, Ext='{file_extension}', MIME='{file_mime_type}'")
        if file_extension not in self.ALLOWED_EXTENSIONS:
            print(f"ERROR: File extension rejected. '{file_extension}' not in allowed list.")
            return Response({
                "status": False,
                "message": f"Unsupported file type. Extension '{file_extension}' is not allowed."
            }, status=400)
        
        if file_mime_type not in self.ALLOWED_MIME_TYPES:
            print(f"WARNING: MIME type '{file_mime_type}' is unexpected but file processing will continue.")
            pass 
            
        try:
            encrypted_data_bytes = uploaded_file.read()
            print(f"   Successfully read {len(encrypted_data_bytes)} bytes.")
            is_base64=is_base64_string(encrypted_data_bytes)
            if not is_base64:
                base64_string=base64.b64encode(encrypted_data_bytes).decode()
            else:
                base64_string=encrypted_data_bytes

            data_bits=convert_to_bits(base64_string)
            if data_bits:
                feed_model=nist_statistical_test(data_bits)
                if feed_model:
                    print(feed_model)
                    return Response({"status":True,"predicted_results":feed_model})
                else:
                    return Response({"status":False,"message":"Error in feeding the data to the model"})
            else:
                return Response({"status":False,"message":"Error in converting encrypted text to bits"})

        except Exception as e:
            print(f"CRITICAL ERROR in Try block: {e.__class__.__name__}: {str(e)}")
            return Response({"status": False, "message": f"Processing error: {str(e)}"}, status=500)