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


def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = CustomUser.objects.filter(email=email).first()

        if user is not None:

            if user.check_password(password):
                login(request, user)

                # Set a cookie
                response = redirect('profile')
                response.set_cookie('user_email', email)
                
                return response
            else:
                error_message = "Invalid username or password"
        else:
            error_message = "Invalid username or password"
    else:
        error_message = ""

    return render(request, 'login.html', {'error_message': error_message})

def profile(request):
    user_email = request.COOKIES.get('user_email')

    return render(request, 'profile.html', {'user_email': user_email})


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

def get_auth_status(request):
    is_logged_in = request.user.is_authenticated
    return JsonResponse({'isLoggedIn': is_logged_in})

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


def rewards(request):
    return render(request, 'rewards.html')
