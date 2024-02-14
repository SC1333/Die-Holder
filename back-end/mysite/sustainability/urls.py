from django.urls import path
from . import Views

app_name = "sustainability"
urlpatterns = [
    path('',Views.home,name='home'), #adds a simple homepage to the default URL path
    path('leaderboard/',Views.leaderboard,name='leaderboard'), #adds a simple homepage to the default URL path
    path('login/',Views.login,name='login'), #adds a simple homepage to the default URL path
    path('map/',Views.map,name='map'), #adds a simple homepage to the default URL path
    path('rewards/',Views.rewards,name='rewards'), #adds a simple homepage to the default URL path
]