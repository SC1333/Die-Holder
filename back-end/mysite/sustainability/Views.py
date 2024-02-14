from django.shortcuts import render
from django.http import HttpResponse
import os

#creating the webpages
def home(request):
    return render(request,'home.html') #renders the html (THIS DOESNT WORK CURRENTLY)
def leaderboard(request):
    return HttpResponse("This is the leaderbard page for the ECM2434 project website")
def login(request):
    return HttpResponse("This is the login page for the ECM2434 project website")
def map(request):
    return HttpResponse("This is the map page for the ECM2434 project website this will display the ownership map for each team")
def rewards(request):
    return HttpResponse("This is the rewards page for the ECM2434 project website users will claim their points from sustainable actions here.")