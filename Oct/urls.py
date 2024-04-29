from django.urls import path
from .views import OctImageUpload, RecentOctImages

urlpatterns = [
    path("uploadimage/", OctImageUpload.as_view(), name="upload-image"),
    path("all-images/", OctImageUpload.as_view(), name="get-all-oct"),
    path("recent-images/", RecentOctImages.as_view(), name="recent-oct-images"),
]
