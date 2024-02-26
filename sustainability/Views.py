from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import RegisterForm
from .models import Stronghold, Action, Team, User, Score,Player
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from collections import defaultdict

# creating the webpages

"""This section renders the html templates for the webpages"""


def home(request):
    return render(request, 'home.html')


def leaderboard(request):
    # Get data from the database
    players = Player.objects.all()

    # Calculate total points for each group
    group_points = defaultdict(int)
    user_points = {}

    for player in players:
        # Get the related user instance
        user = player.user
        # Get all actions done by the user
        user_actions = Score.objects.filter(user=user)
        # Aggregate total points for those actions
        total_points = user_actions.aggregate(total_points=Sum('action_done__points_value'))['total_points'] or 0
        # Apply user's point multiplier
        total_points *= player.pts_multiplier
        # Add total points to the user's group
        group_points[player.team.team_name] += total_points
        # Store individual user points
        user_points[user.username] = total_points

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
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Set a cookie for the username
                response = redirect('/')
                response.set_cookie('userID', user.id, max_age=3600)
                
                return response
            else:
                error_message = "Invalid username or password"
    else:
        form = AuthenticationForm()
        error_message = ""

    return render(request, 'login.html', {'form': form, 'error_message': error_message})
    
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Create a new User instance
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['firstname'],
                last_name=form.cleaned_data['lastname'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
              # Reverse map the selected team color to the corresponding color code
            team_color_code = next(code for code, color in Team.COLORS.items() if color.lower() == form.cleaned_data['team_colour'])
            # Get the Team object based on the color code
            team = Team.objects.get(team_color=team_color_code)
            # Create a new Player instance associated with the User and Team
            player = Player.objects.create(
                user=user,
                team=team
            )
            return redirect('/')  # Redirect to a success page
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
        try:
            userID = request.POST.get('userID')
            buildingID = request.POST.get('buildingID')
            actionID = request.POST.get('actionID')
            dateTimeEarned = request.POST.get('dateTimeEarned')
            
            # Create a new Score object and save it to the database
            score = Score(user=userID, action_site=buildingID, action_done=actionID, datetime_earned=dateTimeEarned)
            score.save()

            # Retrieve building name, action name, and points value
            building_name = Stronghold.objects.get(id=buildingID).name
            action_name = Action.objects.get(id=actionID).name
            points_value = Action.objects.get(id=actionID).points_value

            return JsonResponse({
                'success': True,
                'buildingName': building_name,
                'actionName': action_name,
                'pointsValue': points_value
            })
        except (Stronghold.DoesNotExist, Action.DoesNotExist):
            return JsonResponse({'error': 'Building or Action not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)