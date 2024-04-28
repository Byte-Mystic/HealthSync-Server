from django.db import models
from Accounts.models import CustomUser

# Create your models here.


class MAMMO(models.Model):
    user_mammo_id = models.AutoField(primary_key=True)
    patient_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.URLField()
    result = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Oct {self.user_mammo_id}"
