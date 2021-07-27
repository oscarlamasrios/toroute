from django.db import models

# Create your models here.
class  Route(models.Model):
  date = models.DateField(auto_now=False, auto_now_add=True,editable=False)

class Place(models.Model):
  name = models.CharField(max_length=30)
  lat = models.FloatField()
  lon = models.FloatField()
  identifier = models.CharField(max_length=30)

class RP(models.Model):
  route_id= models.ForeignKey(Route,on_delete=models.CASCADE)
  place_id= models.ForeignKey(Place,on_delete=models.CASCADE)
