from django.contrib import admin
from user.models import User, UserFollowing, UserProfile, PetProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 1

class PetProfileInline(admin.StackedInline):
    model = PetProfile
    extra = 1

class UserAdmin(admin.ModelAdmin):
    list_display = ('id','email', 'username',)
    list_display_links = ('email', 'username',)
    list_filter = ('created_at', 'updated_at')
    search_fields = ('email', 'username',)
    ordering = ('-created_at',)
    list_per_page = 10
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ("정보", {
            'fields': ('email', 'username',)
        
        }),
        ('가입 수정 날짜', {
            'fields': ('created_at', 'updated_at',)
        }),
    )
    inlines = [UserProfileInline, PetProfileInline,]

admin.site.register(User, UserAdmin)
admin.site.register(UserFollowing)
admin.site.register(PetProfile)