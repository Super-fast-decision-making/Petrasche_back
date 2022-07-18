from django.contrib import admin
from dm.models import Message, Header

# Register your models here.

admin.site.register(Message)

class Message(admin.TabularInline):
    model = Message

class HeaderAdmin(admin.ModelAdmin):
    inlines = [Message]
    class Meta:
        model = Header

admin.site.register(Header, HeaderAdmin)
