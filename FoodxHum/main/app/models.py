# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class UserRegister(models.Model):
    location = models.TextField()
    name = models.TextField()
    password = models.TextField()
    phone_number = models.TextField(blank=True, null=True)
    preference = models.JSONField(db_column='preference', blank=True, null=True)  # Field name made lowercase.
    latitude=models.DecimalField(db_column='latitude',decimal_places=6, max_digits=9,null=True,blank=True)
    longitude=models.DecimalField(db_column='longitude',decimal_places=6, max_digits=9,null=True,blank=True)
    class Meta:
        managed = True
        db_table = 'user_register'
class Restaraunt(models.Model):
    location=models.TextField(db_column='Location',null=False)
    restaraunt = models.TextField(db_column='Restaraunt',null=False)  # Keep 'restaraunt' consistently
    latitude=models.DecimalField(db_column='latitude',decimal_places=6, max_digits=9,null=True,blank=True)
    longitude=models.DecimalField(db_column='longitude',decimal_places=6, max_digits=9,null=True,blank=True)
    # menu=models.TextField(db_column='menu')
    # offers=models.TextField(db_column='offers',null=True)
    class Meta:
        managed=True
        db_table="restaraunt"


class Reviews(models.Model):
    class RatingChoices(models.TextChoices):  # IntegerChoices instead of TextChoices
        ONE = "1", "1 - Poor"
        TWO = "2", "2 - Fair"
        THREE = "3", "3 - Good"
        FOUR = "4", "4 - Very Good"
        FIVE = "5", "5 - Excellent"
    user = models.ForeignKey(UserRegister,on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaraunt,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    review_text = models.IntegerField(blank=True, null=True)
    rating=models.TextField(choices=RatingChoices.choices)
#Review.objects.create(user_id=1, restaurant_id=5, review_text="Great food!", rating=5)

    class Meta:
        managed = True
        db_table = 'reviews'
