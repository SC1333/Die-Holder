from django.urls import path
from . import Views

"""This section creates the urls for the webpages"""
app_name = "sustainability"
urlpatterns = [
    path('', Views.home, name='home'),
    path('leaderboard/', Views.leaderboard, name='leaderboard'),
    path('auth/', Views.auth, name='auth'),
    path('login/', Views.login, name='login'),
    path('register/', Views.register, name='register'),
    path('map/', Views.map, name='map'),
    path('rewards/', Views.rewards, name='rewards'),
    path('redeem-points/<int:buildingID>/<int:actionID>/', Views.redeem_points, name='redeem-points'),
    path('get-building-and-action-names/<int:buildingID>/<int:actionID>/', Views.get_building_and_action_names, name='get-building-and-action-names'),#used as a getter for the database
    path('write-to-score-table/', Views.write_to_score_table, name='write-to-score-table'),
]
