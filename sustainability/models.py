import io

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from typing import Optional

from django.db import models
from django.conf import settings

import pyotp
import qrcode
import qrcode.image.svg



class Team(models.Model):
    COLORS = {
        'FF0000': 'Red',
        '0000FF': 'Blue',
        '00FF00': 'Green'
    }
    team_name = models.CharField(max_length=100, primary_key=True)
    team_color = models.CharField(max_length=6, choices=COLORS)


class Stronghold(models.Model):
    building_name = models.CharField(max_length=100, unique=True)
    controlling_team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)


class Coordinate(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    stronghold = models.ForeignKey(Stronghold, on_delete=models.CASCADE)


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
    user = models.ForeignKey(Player, on_delete=models.CASCADE)
    action_site = models.ForeignKey(Stronghold, on_delete=models.CASCADE)
    action_done = models.ForeignKey(Action, on_delete=models.CASCADE)
    datetime_earned = models.DateTimeField()


class AdminTwoFactorAuthData(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='two_factor_auth_data',
        on_delete=models.CASCADE
    )

    otp_secret = models.CharField(max_length=255)

    def generate_qr_code(self, name: Optional[str] = None) -> str:
        totp = pyotp.TOTP(self.otp_secret)
        qr_uri = totp.provisioning_uri(
            name=name,
            issuer_name='sustainability'
        )

        # Create a QR code with a white background
        qr_code_image = qrcode.make(qr_uri, image_factory=qrcode.image.svg.SvgPathFillImage)

        # The result is going to be an HTML <svg> tag
        return qr_code_image.to_string().decode('utf_8')

    def validate_otp(self, otp: str) -> bool:
        totp = pyotp.TOTP(self.otp_secret)

        return totp.verify(otp)