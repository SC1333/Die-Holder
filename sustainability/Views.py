from django.shortcuts import render
from django.http import HttpResponse
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



def rewards(request):
    return HttpResponse("This is the rewards page for the ECM2434 project website users will claim their points from "
                        "sustainable actions here.")
