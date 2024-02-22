from django.contrib import admin
from .models import Team, Stronghold, Coordinate, Action, User, Score

admin.site.register(Team)
admin.site.register(Stronghold)
admin.site.register(Coordinate)
admin.site.register(Action)
admin.site.register(User)
admin.site.register(Score)
