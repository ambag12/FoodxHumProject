from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UserRegisterSerializer,RestarauntSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from django.urls import reverse
import bcrypt
import json
import re
from geopy.geocoders import Photon
import pandas as pd
# # # Create your views here.
from .models import Restaraunt

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def get_dharestaraunts(request):
    if request.method == 'GET':
        restaraunt=pd.read_excel(r'D:\sample_data_for_foodxhum\Karachi\DHA.xlsx',engine='openpyxl')
        max_count=restaraunt['Title'].count()
        data_dict={}
        for i in range(max_count):
            data_dict[restaraunt['Title'][i]] = {
                "name": restaraunt['Title'][i],
                "Reviews": restaraunt['Reviews'][i],
                "Review_Points": restaraunt['Review_Points'][i],
                "Address": restaraunt['Address'][i],
                "Category": restaraunt['Category'][i]
            }
            
        df=pd.DataFrame(data_dict)
        df.to_json('DHA.json',indent=4,index=True)
        df = df.where(pd.notna(df), None)
        return Response({'restraunts':df.to_dict(orient="records"),'none values':df.isna()},status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def get_dharestaraunts_qry(request, restaraunt):
    if request.method == 'GET':
        restaraunt_specific = Restaraunt.objects.get(restaraunt=restaraunt)
        getdata = RestarauntSerializer(restaraunt_specific)
        return Response({'restaraunt data': getdata.data}, status=status.HTTP_200_OK)

@api_view(['GET','POST','PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def restaraunt_x_database(request,restaraunt):
    Area=request.META.get('HTTP_AREA')
    df=pd.read_json(rf"C:\Users\ambai\FoodxHum\main\{Area}.json")
    print({"address":df[restaraunt]['Address']})
    if request.method=='PATCH':
        dest_address=df[restaraunt]['Address']
        cleaned_address = re.sub(r'\b\d+\s*(st|nd|rd|th)?\s*(floor|suite|apartment|apt|room|office|building|R22P|JRG|)\b', '', dest_address, flags=re.IGNORECASE).strip()
        geolocator = Photon(user_agent="foodxhum_geocoder")
        location = geolocator.geocode(cleaned_address,timeout=10)
        if location:
                print("Full Address:", location.address,"\n location.latitude:",location.latitude,"\n location.longitude:",location.longitude)
                lat=location.latitude
                long=location.longitude
                restaraunt_output= (location.latitude, location.longitude)
        else:
                restaraunt_output=None
                lat=None
                long=None
        print(restaraunt_output)
        update_qury=Restaraunt.objects.filter(restaraunt=restaraunt).update(location=str(df[restaraunt]['Address']),latitude=lat,longitude=long)
        if update_qury > 0: 
            updated_instance = Restaraunt.objects.get(restaraunt=restaraunt)  # Fetch updated instance
            serializer = RestarauntSerializer(updated_instance)
            return Response({"Updated record": serializer.data}, status=status.HTTP_200_OK)
        else:
            insert=Restaraunt.objects.create(restaraunt=restaraunt,location=str(df[restaraunt]['Address']),latitude=lat,longitude=long)
            serializer=RestarauntSerializer(insert)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data,status=status.HTTP_201_CREATED)
            return Response({"error":serializer.error_messages},status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        get_qry=Restaraunt.objects.get(restaraunt=restaraunt)
        serializer=RestarauntSerializer(get_qry)
        return Response({'data':serializer.data},status=status.HTTP_200_OK)
    if request.method == "POST":
        restaraunt=pd.read_excel(rf'D:\sample_data_for_foodxhum\Karachi\{Area}.xlsx',engine='openpyxl')
        data_dict = {}
        for i in range(1,10):
            title = restaraunt.loc[i, 'Title']
            dest_address = restaraunt.loc[i, 'Address']
            cleaned_address = re.sub(r'\b\d+\s*(st|nd|rd|th)?\s*(floor|suite|apartment|apt|room|office|building|R22P|JRG|)\b', '', dest_address, flags=re.IGNORECASE)
            dest_address=cleaned_address.strip()
            geolocator = Photon(user_agent="foodxhum_geocoder")
            location = geolocator.geocode(dest_address,timeout=10)
            if location:
                 print("Full Address:", location.address)
                 lat=location.latitude
                 long=location.longitude
                 restaraunt_output= (location.latitude, location.longitude)
            else:
                 restaraunt_output=None
                 lat=None
                 long=None
            print(restaraunt_output)
            data_dict[title] = {
            "name": title,
            "Reviews": restaraunt.loc[i, 'Reviews'],
            "Review_Points": restaraunt.loc[i, 'Review_Points'],
            "Address": dest_address,
            "Category": restaraunt.loc[i, 'Category'],
            "Latitude": lat,
            "Longitude": long
    }
            print(data_dict)
            query=Restaraunt.objects.create(restaraunt=title,location=dest_address,latitude=round(lat, 6) if lat is not None else None,longitude=round(long, 6) if long is not None else None)
            serializer=RestarauntSerializer(data=query)
            if query and serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data,status=status.HTTP_201_CREATED)
        data_dict=json.dumps(data_dict)
        return JsonResponse(json.loads(data_dict),status=status.HTTP_201_CREATED)
    
