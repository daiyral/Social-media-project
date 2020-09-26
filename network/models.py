from django.contrib.auth.models import AbstractUser
from django.db import models
import json

class User(AbstractUser):
    following=models.ManyToManyField('User',blank=True,related_name="my_followed")
    followers=models.ManyToManyField('User',blank=True,related_name="my_follwers")
    picture=models.ImageField(upload_to='profile_picture',blank=True,default='blank-profile-picture.png')
    liked=models.ManyToManyField('Post',blank=True,related_name="liked_post") 

    

class Post(models.Model):
    text=models.CharField(max_length=256)
    poster=models.ForeignKey(User,on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now=False,auto_now_add=True)
    likes=models.IntegerField(default=0)
    liked_by=models.ManyToManyField(User,blank=True,related_name="likers")

    def serialize(self):
        return{
            'id':self.id,
            'text':self.text,
            'poster':self.poster.username
        }
    def __str__(self):
        return f'{self.poster} posted {self.text}'