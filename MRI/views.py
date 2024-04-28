import os

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import requests
import copy
from .serializers import MRISerializer
from .models import MRI
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from keras import backend as k
import cv2
from keras.api.models import load_model
import numpy as np

JWT_authenticator = JWTAuthentication()

class MRIImageUpload(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            recent_mri_images = MRI.objects.order_by("-created-at")
            serializer = MRISerializer(recent_mri_images, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        img = request.data["image"]
        # prediction = MRIPrediction(copy.deepcopy(img))
        response = JWT_authenticator.authenticate(request)
        if response is None:
            return Response(
                {"error": "User Not Found."}, status=status.HTTP_401_UNAUTHORIZED
            )
        patient, _ = response
        img = request.data["image"]
        serializer = MRISerializer(data=request.data)
        image_upload_url = "https://api.imgur.com/3/image"
        headers = {
            "Authorization": f"Client-ID {config('IMGUR_CLIENT_ID')}",
        }
        response = requests.post(
            image_upload_url, headers=headers, files={"image": img}
        )

        if response.status_code == 200:
            imgur_data = response.json()
            imgur_url: str = imgur_data["data"]["link"]
            data = {"image": imgur_url, "patient_id": patient.pk, "result": prediction}
            serializer = MRISerializer(data=data)
            if serializer.is_valid():
                oct = MRI(**serializer.validated_data) 
                oct.save()
                return Response("Result Generated.", status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_425_TOO_EARLY)
        else:
            return Response(
                {"message": response.text, "error": "Image upload failed"},
                status=response.status_code,
            )


class RecentMRIImages(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            recent_mri_images = MRI.objects.order_by("-created-at")[:3]
            serializer = MRISerializer(recent_mri_images, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
