from django.contrib import admin
from .models import Team, Stronghold, Action, User, Score, Player
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
admin.site.register(Team)
admin.site.register(Stronghold)
admin.site.register(Action)
admin.site.register(Score)

class PlayerInline(admin.StackedInline):
    model = Player
    can_delete = False
    verbose_name_plural = 'player'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (PlayerInline,)

# Unregister the default UserAdmin
admin.site.unregister(User)

# Register User with your custom admin
admin.site.register(User, CustomUserAdmin)
