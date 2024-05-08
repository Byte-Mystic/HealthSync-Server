import os

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import requests
import copy
from .serializers import MAMMOSerializer
from .models import MAMMO
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import cv2
from PIL import Image
import torch
from torchvision import models, transforms
import numpy as np

JWT_authenticator = JWTAuthentication()

script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "Resnet_fineTuning.pth")
print(model_path)
model = torch.load(model_path, map_location=torch.device("cpu"))


def MammoPrediction(image):
    try:
        class_names = ["benign", "malignant", "normal"]
        transform = transforms.Compose(
            [
                transforms.Resize(
                    256
                ),  # Resize to a larger size for better preprocessing
                transforms.CenterCrop(224),  # Crop the center of the resized image
                transforms.ToTensor(),  # Convert to tensor
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),  # Normalize (ImageNet statistics)
            ]
        )
        image = Image.open(image)
        preprocessed_image = transform(image)
        image_batch = preprocessed_image.unsqueeze(0)
        with torch.no_grad():
            output = model(image_batch)
        predicted_class = torch.argmax(output.data, dim=1)
        return class_names[predicted_class.item()]
    except Exception as e:
        print(f"Error in Predicting Mammo: {e}")


class MAMMOImageUpload(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            recent_mammo_images = MAMMO.objects.order_by("-created_at")
            serializer = MAMMOSerializer(recent_mammo_images, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        img = request.data["image"]
        prediction = MammoPrediction(copy.deepcopy(img))
        response = JWT_authenticator.authenticate(request)
        if response is None:
            return Response(
                {"error": "User Not Found."}, status=status.HTTP_401_UNAUTHORIZED
            )
        patient, _ = response
        img = request.data["image"]
        serializer = MAMMOSerializer(data=request.data)
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
            serializer = MAMMOSerializer(data=data)
            if serializer.is_valid():
                oct = MAMMO(**serializer.validated_data)
                oct.save()
                return Response("Result Generated.", status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_425_TOO_EARLY)
        else:
            return Response(
                {"message": response.text, "error": "Image upload failed"},
                status=response.status_code,
            )


class RecentMAMMOImages(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            recent_mammo_images = MAMMO.objects.order_by("-created_at")[:3]
            serializer = MAMMOSerializer(recent_mammo_images, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
