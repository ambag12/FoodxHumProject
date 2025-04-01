from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UserRegisterSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from django.urls import reverse
from geopy.geocoders import Photon
import re
from geopy.distance import geodesic
# import requests
import bcrypt
import json
# Create your views here.
from .models import *

@api_view(['POST'])
@permission_classes([AllowAny])
def Register(request):
    if request.method == 'POST':
        pref=request.data.get('preference')
        name=request.data.get('name')
        password=request.data.get('password')
        b_password=password.encode('utf-8')
        newinstance,created=User.objects.get_or_create(username=name,defaults={'last_login': timezone.now()})
        print('newinstance',newinstance,'created',created)
        if created:
            newinstance.set_password(password) 
            newinstance.save()
        hashed_password = bcrypt.hashpw(b_password, bcrypt.gensalt())
        if pref:
            pref_list=json.dumps(pref)
        else:
            pref_list=json.dumps([])
        user_data={
                'name':name,
                'password':hashed_password.decode('utf-8'),
                'preference':pref_list,
                'location':request.data.get('location'),
                'phone_number':request.data.get('phone_number')
            }
        print('Serailizer for json body LOG:',user_data)
        serializer = UserRegisterSerializer(data=user_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class UserLogin(APIView):
    def post(self, request):
        try:
            user=request.data.get('name')
            password=request.data.get('password')
            users = UserRegister.objects.get(name=user)
            encoded_password=users.password.encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'),encoded_password):
                token_url = reverse('token_obtain_pair')
                token_url = request.build_absolute_uri(token_url)
                payload = {'username': user, 'password': password}
                token_response = request.post(token_url, json=payload)
                if token_response.status_code == 200:
                    request.session['auth_token'] = token_response.json()['access']
                    return Response({
                        'message': 'Login successful',
                        'token': token_response.json()['access'],
                        'token_refresh': token_response.json()['refresh']
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'error': f'Invalid credentials token not generated, {token_response.status_code} and {token_response.text}'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"error": "Invalid password!"}, status=status.HTTP_401_UNAUTHORIZED)
        except Register.DoesNotExist:
            return Response({"error": "User not found!"}, status=status.HTTP_404_NOT_FOUND)    

@api_view(['GET'])    
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def Userreg_list(request):
    if request.method=="GET":
        get_all=UserRegister.objects.all()
        serializer=UserRegisterSerializer(get_all,many=True)
        return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def user_preferences(request):
    if request.method=='POST':
        location=request.data.get('location')
        #user location
        cleaned_address = re.sub(r'\b\d+\s*(st|nd|rd|th)?\s*(floor|suite|apartment|apt|room|office|building)\b', '', location, flags=re.IGNORECASE)
        user_address=cleaned_address.strip()
        geolocator = Photon(user_agent="foodxhum_geocoder")
        location = geolocator.geocode(user_address,timeout=10)
        if location:
            print("Full Address:", location.address)
            output= (location.latitude, location.longitude)
        else:
            output=None
            print(output)
        if re.search(rf"\b(DHA|Defence Housing Authority)\b",user_address):
            qry=Restaraunt.objects.raw("""
SELECT id, restaraunt, latitude, longitude,
       ST_Distance_Sphere(
           POINT(longitude, latitude),  
           POINT(%s, %s)
       ) / 1000 AS distance_km
FROM restaraunt
WHERE ST_Distance_Sphere(
           POINT(longitude, latitude),
           POINT(%s, %s)
       ) / 1000 < 50;
""", [location.longitude, location.latitude, location.longitude, location.latitude])

        restaurant_list=[restaurant.restaraunt for restaurant in qry]
        # distance_output=geodesic(output, destoutput).km
        # print(f'{distance_output}km')
        return Response({"restaurants": restaurant_list})
