from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import RegisterForm
from .models import Stronghold, Action, User, Score
from django.db.models import Sum
from collections import defaultdict

# creating the webpages

"""This section renders the html templates for the webpages"""


def home(request):
    return render(request, 'home.html')


def leaderboard(request):
    # Get data from the database
    users = User.objects.all()

    # Calculate total points for each group
    group_points = defaultdict(int)
    user_points = {}

    for user in users:
        # Get all actions done by the user
        user_actions = Score.objects.filter(user=user)
        # Aggregate total points for those actions
        total_points = user_actions.aggregate(total_points=Sum('action_done__points_value'))['total_points'] or 0
        # Apply user's point multiplier
        total_points *= user.pts_multiplier
        # Add total points to the user's group
        group_points[user.team.team_name] += total_points
        # Store individual user points
        user_points[user] = total_points

    # Convert defaultdict to regular dict
    group_points = dict(group_points)

    # Sort users by total points
    sorted_users = sorted(user_points.items(), key=lambda x: x[1], reverse=True)
    # Sort groups by total points
    sorted_groups = sorted(group_points.items(), key=lambda x: x[1], reverse=True)

    return render(request, 'leaderboard.html', {'sorted_users': sorted_users, 'sorted_groups': sorted_groups})


def auth(request):
    return render(request, 'auth.html')


def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # User is authenticated, log them in
            login(request, user)

            # Set a cookie for the username
            response = redirect('profile')
            response.set_cookie('username', user.username)

            return response
        else:
            error_message = "Invalid username or password"
    else:
        error_message = ""

    return render(request, 'login.html', {'error_message': error_message})
    
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():

            username = form.cleaned_data['username']
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            dob = form.cleaned_data['dob']
            email = form.cleaned_data['email']
            team_colour = form.cleaned_data['team_colour']
            password = form.cleaned_data['password']
            
            new_user = User.objects.create_user(username=username, first_name=firstname, last_name=lastname, dob=dob, email=email, team_color=team_colour, password=form.cleaned_data['password'])
            new_user.save()

            # Redirect to login or any other page after successful registration
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def map(request):
    return render(request, 'map.html')


def redeem_points(request, buildingID, actionID):
    context = {
        'buildingID': buildingID,
        'actionID': actionID,
    }
    return render(request, 'redeem_points.html', context)

def get_building_and_action_names(request, buildingID, actionID):
    try:
        building = Stronghold.objects.get(id=buildingID)
        action = Action.objects.get(id=actionID)
        
        data = {
            'buildingName': building.building_name,
            'actionName': action.action_name
        }
        return JsonResponse(data)
    except (Stronghold.DoesNotExist, Action.DoesNotExist):
        return JsonResponse({'error': 'Building,Action or User not found'}, status=404)


def write_to_score_table(request):
    if request.method == 'POST':
        userID = request.POST.get('userID')
        buildingID = request.POST.get('buildingID')
        actionID = request.POST.get('actionID')
        dateTimeEarned = request.POST.get('dateTimeEarned')
        
        # Create a new Score object and save it to the database
        score = Score(user=userID, action_site=buildingID, action_done=actionID, datetime_earned=dateTimeEarned)
        score.save()
        
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)