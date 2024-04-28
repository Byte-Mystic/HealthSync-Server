from django.urls import path
from .views import MAMMOImageUpload, RecentMAMMOImages

urlpatterns = [
    path("uploadimage/", MAMMOImageUpload.as_view(), name="upload-image"),
    path("all-mammo/", MAMMOImageUpload.as_view(), name="get-all-mammo"),
    path("recent-mammo-images/", RecentMAMMOImages.as_view(), name="recent-mammo-images"),
]
