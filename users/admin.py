# users/admin.py

from django.contrib import admin
from .models import UserProfile, LoginHistory

class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'ip_address')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('user', 'timestamp', 'ip_address')

admin.site.register(UserProfile)
admin.site.register(LoginHistory, LoginHistoryAdmin)