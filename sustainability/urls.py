from django.urls import path
from . import Views
from django.contrib.auth.models import User
from django_otp.admin import OTPAdminSite
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from .Views import custom_logout

class OTPAdmin(OTPAdminSite):
    pass


adminSite = OTPAdmin(name='OTPAdmin')
adminSite.register(User)
adminSite.register(TOTPDevice,TOTPDeviceAdmin)


"""This section creates the urls for the webpages"""
app_name = "sustainability"
urlpatterns = [
    path('', Views.home, name='home'),
    path('leaderboard/', Views.leaderboard, name='leaderboard'),
    path('auth/', Views.auth, name='auth'),
    path('login/', Views.log_in, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('otplogin/', Views.otp_login, name='otplogin'),
    path('register/', Views.register, name='register'),
    path('map/', Views.map, name='map'),
    path('redeem-points/<int:buildingID>/<int:actionID>/', Views.redeem_points, name='redeem-points'),#used as a getter for the database via a jquery request
    path('get-building-and-action-names/<int:buildingID>/<int:actionID>/', Views.get_building_and_action_names, name='get-building-and-action-names'),#used as a getter for the database via a jquery request
    path('write-to-score-table/', Views.write_to_score_table, name='write-to-score-table'),#used to write to the database score table via a jquery request
    path('setup/', Views.generate_totp_secret, name='setup'),
    path('check-cookie/', Views.check_cookie, name='check_cookie'),
    path('privacy/', Views.privacy, name='privacy'),
]
