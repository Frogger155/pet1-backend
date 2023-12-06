from django.db import models
from accounts.models import CustomUser

class Tag(models.Model):

    name = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.name

class Post(models.Model):

    def uploader_switch(instance, filename):
        VIDEO_FORMATS = ("mp4", "mov", "avi", "webm")
        PICTURE_FORMATS = ["png", "jpeg", "jpg", "gif"]
        filenameExtension = filename.split(".")[1]
        if filenameExtension in VIDEO_FORMATS:
            return "videos/{0}".format(filename)
        elif filenameExtension in PICTURE_FORMATS:
            return "pictures/{0}".format(filename)

    def __str__(self):
        return self.title    

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200, null=False, blank=False)
    content = models.FileField(upload_to=uploader_switch, blank=False, null=False)
    tags = models.ManyToManyField(Tag)

