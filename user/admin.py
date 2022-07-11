from django.contrib import admin
from user.models import User, UserFollowing, UserProfile, PetProfile

# Register your models here.
admin.site.register(User)
admin.site.register(UserFollowing)
admin.site.register(UserProfile)

admin.site.register(PetProfile)