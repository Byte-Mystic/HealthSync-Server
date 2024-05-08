from django.urls import path
from .views import MRIImageUpload, RecentMRIImages

urlpatterns = [
    path("uploadimage/", MRIImageUpload.as_view(), name="upload-image"),
    path("all-images/", MRIImageUpload.as_view(), name="get-all-mri"),
    path("recent-images/", RecentMRIImages.as_view(), name="recent-mri-images"),
]
