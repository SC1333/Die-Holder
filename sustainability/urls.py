from django.urls import path
from . import Views

"""This section creates the urls for the webpages"""
app_name = "sustainability"
urlpatterns = [
    path('', Views.home, name='home'),
    path('leaderboard/', Views.leaderboard, name='leaderboard'),
    path('auth/', Views.auth, name='auth'),
    path('login/', Views.log_in, name='login'),
    path('register/', Views.register, name='register'),
    path('map/', Views.map, name='map'),
    path('redeem-points/<int:buildingID>/<int:actionID>/', Views.redeem_points, name='redeem-points'),
    path('get-building-and-action-names/<int:buildingID>/<int:actionID>/', Views.get_building_and_action_names, name='get-building-and-action-names'),
    path('write-to-score-table/', Views.write_to_score_table, name='write-to-score-table'),
    path('password_reset/', Views.password_reset_request, name='password_reset_request'),
    path('password_reset/done/', Views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', Views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', Views.password_reset_complete, name='password_reset_complete'),
]
