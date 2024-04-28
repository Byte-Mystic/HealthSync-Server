from django.urls import path
from .views import MRIImageUpload, RecentMRIImages

urlpatterns = [
    path("upload-mri-image/", MRIImageUpload.as_view(), name="upload-image"),
    path("all-mri/", MRIImageUpload.as_view(), name="get-all-mri"),
    path("recent-mri-images/", RecentMRIImages.as_view(), name="recent-mri-images"),
]
