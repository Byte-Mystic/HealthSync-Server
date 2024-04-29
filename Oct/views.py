import os

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import requests
import copy
from .serializers import OctSerializer
from .models import Oct
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from keras import backend as k
import cv2
from keras.api.models import load_model
import numpy as np


script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "DenseNet121.hdf5")
# model = load_model(model_path)

JWT_authenticator = JWTAuthentication()


def OCTPrediction(uploaded_image):
    """
    This function includes entire pipeline, from data preprocessing to making final predictions.
    Input: Image
    Output: Predictions for the input
    """
    try:
        file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        image = cv2.resize(image, (244, 244))
        image = image.astype(np.float32)
        image = image / 255.0
        image = np.expand_dims(image, axis=0)

        if model is None:
            return "Model is not Loaded"

        pred = model.predict(image)
        class_labels = ["CNV", "DME", "DRUSEN", "NORMAL"]
        predicted_index = np.argmax(pred, axis=1)
        predicted_class_label = class_labels[predicted_index[0]]
        k.clear_session()
        return predicted_class_label
    except Exception as e:
        return Response(
            {"error": f"Error in Prediction {e}"}, status=status.HTTP_400_BAD_REQUEST
        )


class OctImageUpload(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            recent_oct_images = Oct.objects.order_by("-created_at")
            serializer = OctSerializer(recent_oct_images, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        img = request.data["image"]
        prediction = OCTPrediction(copy.deepcopy(img))
        response = JWT_authenticator.authenticate(request)
        if response is None:
            return Response(
                {"error": "User Not Found."}, status=status.HTTP_401_UNAUTHORIZED
            )
        patient, _ = response
        img = request.data["image"]
        serializer = OctSerializer(data=request.data)
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
            serializer = OctSerializer(data=data)
            if serializer.is_valid():
                oct = Oct(**serializer.validated_data)  # type: ignore
                oct.save()
                return Response("Result Generated.", status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_425_TOO_EARLY)
        else:
            return Response(
                {"message": response.text, "error": "Image upload failed"},
                status=response.status_code,
            )


class RecentOctImages(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            recent_oct_images = Oct.objects.order_by("-created_at")[:3]
            serializer = OctSerializer(recent_oct_images, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
