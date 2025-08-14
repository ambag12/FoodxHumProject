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
import json,os,requests
import re
from geopy.geocoders import Photon
import pandas as pd
from django.conf import settings
from requests.exceptions import JSONDecodeError as RequestsJSONDecodeError
from .models import Restaraunt
from main.settings import BASE_DIR
import environ,math
import numpy as np

env= environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

def _normalize_value(v):
    # handle pandas/numpy missing values and numpy scalars
    if isinstance(v, (np.generic,)):
        v = v.item()
    if isinstance(v, float):
        # catches both float('nan') and normal floats
        return None if math.isnan(v) else v
    if pd.isna(v):
        return None
    return v

def _normalize(obj):
    # recursively normalize dicts/lists
    if isinstance(obj, dict):
        return {k: _normalize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalize(v) for v in obj]
    return _normalize_value(obj)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def get_dharestaraunts(request):
    area=request.query_params.get('area', 'Bahadurabad')
    file_path = rf"D:\DataSet\Karachi\{area}.xlsx"
    if not os.path.isfile(file_path):
        return Response({"error": "Data file not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        df = pd.read_excel(file_path, engine='openpyxl')
    except Exception as e:
        return Response({"error": "Failed to parse Excel file.", "detail": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    cols = ['Title', 'Reviews', 'Review_Points', 'Address', 'Category']
    df = df.reindex(columns=cols)  # keep columns safe if some are missing

    # convert to list-of-dicts and normalize once (fast & simple)
    records = df.rename(columns={'Title': 'name'}).to_dict(orient='records')
    restaurants = [_normalize(r) for r in records]

    return Response({area: restaurants}, status=status.HTTP_200_OK)

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
def restaraunt_x_database(request):
    try:
        file_url = env('File_url')
        data=requests.get(file_url)
        data.raise_for_status()
        df= data.json()
        print("df:", df)
        # new_dict = {}
        # df_count= len(df['Bahadurabad'])
        # i=0
        # list_of_restaraunts = []
        # while i =< df_count:
        #     list_of_restaraunts.append({"name":df['Bahadurabad'][i]['name'],"address":df['Bahadurabad'][i]['Address']})
        #     i += 1
        # print("list_of_restaraunts:", list_of_restaraunts)
    except (RequestsJSONDecodeError, requests.RequestException):
        return Response({"error": "Failed to fetch or parse data from the URL."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if request.method == "GET":
        restaraunt=request.GET.get("restaraunt", None)
        if restaraunt:
            get_qry=Restaraunt.objects.filter(restaraunt=restaraunt).first()
            serializer=RestarauntSerializer(get_qry)
            return Response({'data':serializer.data},status=status.HTTP_200_OK)
        return Response({'data':"Request made "},status=status.HTTP_200_OK)
    if request.method == "POST":
        data_dict = {}
        created=[]
        for i in range(0,10):
            title = df['Bahadurabad'][str(i)]['name']
            dest_address = df['Bahadurabad'][str(i)]['Address']
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
            "restaraunt": title,
            "location": dest_address,
            "latitude": round(lat, 6) if lat is not None else None,
            "longitude": round(long, 6) if long is not None else None
            }
            obj_data={
            "restaraunt": title,
            "location": dest_address,
            "latitude": round(lat, 6) if lat is not None else None,
            "longitude": round(long, 6) if long is not None else None
            }
            print(df)
            serializer=RestarauntSerializer(data=obj_data)
            if obj_data and serializer.is_valid():
                serializer.save()
                created.append(serializer.data)
        data_dict=json.dumps(data_dict)
        return JsonResponse({"data":created},status=status.HTTP_201_CREATED)
    
