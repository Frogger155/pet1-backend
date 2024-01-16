from django.contrib import admin
from .models import *

class LikeAdmin(admin.ModelAdmin):
    pass

class TagsInline(admin.TabularInline):
    model = Post.tags.through

class PostAdmin(admin.ModelAdmin):
    inlines = [
        TagsInline,

    ]
    exclude = ["tags"]

class TagAdmin(admin.ModelAdmin):
    inlines = [
        TagsInline
    ]
    exclude = ["tags"]


admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Like, LikeAdmin)
