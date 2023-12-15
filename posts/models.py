from django.db import models
from accounts.models import CustomUser
import os


class Tag(models.Model):

    name = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.name


class Post(models.Model):
    VIDEO_FORMATS = (".mp4", ".mov", ".avi", ".webm")
    PICTURE_FORMATS = (".png", ".jpeg", ".jpg", ".gif")

    def uploader_switch(instance, filename):
        filenameExtension = os.path.splitext(filename)[1]
        if filenameExtension in Post.VIDEO_FORMATS:
            return "videos/{0}".format(filename)
        elif filenameExtension in Post.PICTURE_FORMATS:
            return "pictures/{0}".format(filename)
       
    @property
    def contentFileExtension(self):
        """Get the file extension"""
        extension = os.path.splitext(self.content.path)[1]
        if extension in Post.VIDEO_FORMATS:
            return "video"
        elif extension in Post.PICTURE_FORMATS:
            return "picture"
        return "unknown"

    def __str__(self):
        return self.title + " Type of content: " + self.getFileExtension()

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200, null=False,
                             blank=False)
    content = models.FileField(
        upload_to=uploader_switch, blank=False, null=False)
    tags = models.ManyToManyField(Tag)