from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Stronghold, Action, User, Score

# creating the webpages

"""This section renders the html templates for the webpages"""


def home(request):
    return render(request, 'home.html')


def leaderboard(request):
    # Get data from the database
    users = User.objects.all()
    # Calculate total points for each user
    user_points = {user: Score.objects.filter(user=user).count() for user in users}
    # Sort users by total points
    sorted_users = sorted(user_points.items(), key=lambda x: x[1], reverse=True)
    return render(request, 'leaderboard.html', {'sorted_users': sorted_users})


def auth(request):
    return render(request, 'auth.html')


def login(request):
    return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')


def map(request):
    return render(request, 'map.html')


def redeem_points(request, buildingID, actionID):
    context = {
        'buildingID': buildingID,
        'actionID': actionID,
    }
    return render(request, 'redeem_points.html', context)


def get_building_and_action_names(request, buildingID, actionID,userID):
    try:
        building = Stronghold.objects.get(id=buildingID)
        action = Action.objects.get(id=actionID)
        user = User.objects.get(id=userID)
        data = {
            'buildingName': building.building_name,
            'actionName': action.action_name,
            'userName': user.full_name
        }
        return JsonResponse(data)
    except (Stronghold.DoesNotExist, Action.DoesNotExist):
        return JsonResponse({'error': 'Building,Action or User not found'}, status=404)


def rewards(request):
    return render(request, 'rewards.html')
