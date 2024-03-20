import uuid
from django.contrib.auth.models import User
from typing import Optional
from django.db import models
from django.conf import settings
import pyotp
import qrcode
import qrcode.image.svg

"""Written by Timothy John Low and Thomas Shannon"""


class Team(models.Model):
    team_name = models.CharField(max_length=100, primary_key=True)
    team_color = models.CharField(max_length=6)


class Stronghold(models.Model):
    building_name = models.CharField(max_length=100, unique=True)
    controlling_team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    mapbox_id = models.IntegerField()


class Action(models.Model):
    action_name = models.CharField(max_length=100)
    points_value = models.IntegerField()


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateTimeField(null=True)
    role = models.CharField(max_length=32)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    pts_multiplier = models.FloatField(default=1.0)
    is_2fa_enabled = models.BooleanField(default=False)


class Score(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    action_site = models.ForeignKey(Stronghold, on_delete=models.CASCADE)
    action_done = models.ForeignKey(Action, on_delete=models.CASCADE)
    datetime_earned = models.DateTimeField()


class AdminTwoFactorAuthData(models.Model):  # creating a new model to store admin 2fa
    user = models.OneToOneField(  # defining the parent table
        settings.AUTH_USER_MODEL,
        related_name='two_factor_auth_data',
        on_delete=models.CASCADE
    )
    # defining the schema
    otp_secret = models.CharField(max_length=255)
    session_identifier = models.UUIDField(blank=True, null=True)

    def generate_qr_code(self, name: Optional[
        str] = None) -> str:  # function to produce the 2fa QR code for authenticator apps
        totp = pyotp.TOTP(self.otp_secret)  # generate the TOTP secret
        qr_uri = totp.provisioning_uri(  # creating the URI stored in the QR code
            name=name,
            issuer_name='sustainability'
        )

        # Create a QR code with a white background
        qr_code_image = qrcode.make(qr_uri, image_factory=qrcode.image.svg.SvgPathFillImage)

        # The result is going to be an HTML <svg> tag
        return qr_code_image.to_string().decode('utf_8')

    def validate_otp(self, otp: str) -> bool:  # checks the otp provided
        totp = pyotp.TOTP(self.otp_secret)

        return totp.verify(otp)

    def rotate_session_identifier(self):  # assigns the 2fa cookie
        self.session_identifier = uuid.uuid4()

        self.save(update_fields=["session_identifier"])
