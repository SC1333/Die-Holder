from django.db import models


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


class User(models.Model):
    username = models.CharField(max_length=100, primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=86)
    salt = models.CharField(max_length=24)
    full_name = models.CharField(max_length=100)
    birthdate = models.DateField()
    role = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    pts_multiplier = models.FloatField(default=1.0)


class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_site = models.ForeignKey(Stronghold, on_delete=models.CASCADE)
    action_done = models.ForeignKey(Action, on_delete=models.CASCADE)
    datetime_earned = models.DateTimeField()
