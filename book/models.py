from django.db import models
from user.models import User

# Create your models here.
class Books(models.Model):
    title = models.CharField(max_length=50, null=False)
    author = models.CharField(max_length=50, null=False)
    price = models.IntegerField(null=False)
    quantity = models.IntegerField(null=False)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    
    class Meta:
        db_table = 'books'
