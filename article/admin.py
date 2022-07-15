from django.contrib import admin
from article.models import Article, Comment, Image
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from user.models import BaseModel, User


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    list_display_links = ('title',)
    list_filter = ('user', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'user__username')
    ordering = ('-created_at',)
    list_per_page = 10
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ("정보", {
            'fields': ('title', 'content', 'user',)
        }),
        # ('작성 정보', {
        #     'fields': ('created_at', 'updated_at',)
        # }),
    )
    inlines = [ImageInline, CommentInline]


# Register your models here.
admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment)
# admin.site.register(Image)