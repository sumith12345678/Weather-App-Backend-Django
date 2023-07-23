from django.contrib.auth import authenticate

from rest_framework.views import APIView,Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from . serializers import *
from . models import *
import random
import string
import requests
import json

from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives

def generatepwd(email):
    chars=string.ascii_letters
    num=string.digits
    all=chars+num
    length=5
    temp=random.sample(all,length)
    temp2="".join(temp)

    if email is not None:
        mail= email.split("@")
        mail2=mail[0]
        pwd=mail2+temp2
        return(pwd)

def sending_mail(email,pwd,username):
    subject = 'login to Weather Plus:'
    message = 'To log in to your account, please click the link http://127.0.0.1:3000/ and Enter your login credentials, including your username :<b>'+username+'</b> and password :<b>'+pwd+'</b> , to access your account securely'
    email_from = settings.EMAIL_HOST_USER
    email_to = [email]
    send_mail(subject, "",email_from,email_to, html_message=message)

class UserRegister(APIView):
    authentication_classes=[]
    permission_classes=[AllowAny,]

    def post(self,request):
        username=request.data.get('username')
        email=request.data.get('email')

        if not User.objects.filter(email=email):
            pwd = generatepwd(email)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=pwd,
            )
            user_serializer=UserSerializer(user)

            sending_mail(email,pwd,username)
            data = {
                'user':user_serializer.data,
            }
            return Response(
                {
                'success': True,
                    'data': data,
                    'message': 'Welcome to Weather Plus, Please check your mail.',
                    'errors': None 
                }
            )
        return Response(
                {
                    'success': False,
                    'data': None,
                    'message': 'This email is already associated with an account ',
                    'errors': None
                }
            )


class UserLogin(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        # print(username)
        # print(password)
        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {
                    'success': False,
                    'data': None,
                    'message': 'Invalid username or password, Please try again',
                    'errors': 'Invalid credentials'
                },
            )

        token, _ = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        serializer_data = serializer.data
        serializer_data['token'] = token.key
        return Response(
            {
                'success': True,
                'data': serializer_data,
                'message': 'You are successfully logged in',
                'errors': None
            }
        )
        

class UserLogout(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            request.user.auth_token.delete()    
            return Response(
                {
                    'success': True,
                    'data': None,
                    'message': 'You have successfully logged out!',
                    'errors': None
                }
            ) 
        except:
            return Response(
            {
                'success': False,
                'data': None,
                'message': 'Oops ,Try Again',
                'errors': None
            }
        )       


def weather_api(city):

    url = "http://api.weatherstack.com/current?access_key=5dba4519f868c50c393ec34be9a64e35&query="+city

    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    response = json.loads(response.text)
    try:
        if response['request'] :
            response['success']=True
        return response
    except:
        return response
        

class SearchWeather(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]

    def get(self, request):
        city = request.GET.get('city')
        data = weather_api(city)
        
        success = data['success']
        if success:
            return Response(
                {
                    'success': True,
                    'data': data,
                    'message': 'Weather Plus',
                    'errors': None
                }
            )
        return Response(
            {
                'success': False,
                'data': None,
                'message': 'Oops City not found or registered in api !!!!',
                'errors': None
            }
        )
        
        
