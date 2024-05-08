import requests
from .serializers import MRISerializer
import os
from .models import MRI
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import tensorflow as tf
import copy
import numpy as np
from PIL import Image


JWT_authenticator = JWTAuthentication()


class MRIImageUpload(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            recent_mri_images = MRI.objects.order_by("-created_at")
            serializer = MRISerializer(recent_mri_images, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, "mri.h5")
        model = tf.keras.models.load_model(model_path)
        img = request.data["image"]
        labels = ["glioma", "meningioma", "notumor", "pituitary"]
        image = Image.open(copy.deepcopy(img))
        resized_img = image.resize((299, 299))
        img = np.asarray(resized_img)
        img = np.expand_dims(img, axis=0)
        img = img / 255
        prediction = model.predict(img)
        probs = list(prediction[0])
        prediction = labels[probs.index(max(probs))]
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
            "Authorization": "Client-ID 5691919050247e1",
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
            recent_mri_images = MRI.objects.order_by("-created_at")[:3]
            serializer = MRISerializer(recent_mri_images, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
