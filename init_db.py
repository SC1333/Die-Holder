from sustainability.models import *


def init_db():
    Stronghold.objects.all().delete()
    User.objects.all().delete()
    Score.objects.all().delete()
    Coordinate.objects.all().delete()
    Action.objects.all().delete()
    Team.objects.all().delete()

    team_green = Team.objects.create(team_name='Green', team_color='00FF00')
    team_red = Team.objects.create(team_name='Red', team_color='FF0000')
    team_blue = Team.objects.create(team_name='Blue', team_color='0000FF')
    team_green.save()
    team_red.save()
    team_blue.save()

    building1 = Stronghold.objects.create(building_name='Building 1')
    building2 = Stronghold.objects.create(building_name='Building 2', controlling_team=team_green)
    building3 = Stronghold.objects.create(building_name='Building 3', controlling_team=team_red)
    building1.save()
    building2.save()
    building3.save()

    user1 = User.objects.create(
        email='user1@test.net',
        password='password1',
        salt='salt1',
        full_name='User One',
        birthdate='1990-01-01',
        role='Student',
        team=team_green,
        pts_multiplier=1
    )
    user2 = User.objects.create(
        email='user2@test.net',
        password='password2',
        salt='salt2',
        full_name='User Two',
        birthdate='2000-01-21',
        role='Student',
        team=team_red,
        pts_multiplier=1
    )
    user3 = User.objects.create(
        email='user3@test.net',
        password='password3',
        salt='salt3',
        full_name='User Three',
        birthdate='1991-12-01',
        role='Student',
        team=team_blue,
        pts_multiplier=1
    )
    user1.save()
    user2.save()
    user3.save()
