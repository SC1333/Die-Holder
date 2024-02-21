from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Stronghold, Action,User
# creating the webpages

"""This section renders the html templates for the webpages"""
def home(request):
    return render(request, 'home.html')


def leaderboard(request):
    return render(request, 'leaderboard.html')


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

def get_building_and_action_names(request, buildingID, actionID,Username):
    try:
        building = Stronghold.objects.get(id=buildingID)
        action = Action.objects.get(id=actionID)
        user = User.objects.get(username=Username)
        data = {
            'buildingName': building.building_name,
            'actionName': action.action_name,
            'userName': user.username
        }
        return JsonResponse(data)
    except (Stronghold.DoesNotExist, Action.DoesNotExist):
        return JsonResponse({'error': 'Building,Action or User not found'}, status=404)

def rewards(request):
    return HttpResponse("This is the rewards page for the ECM2434 project website users will claim their points from "
                        "sustainable actions here.")
