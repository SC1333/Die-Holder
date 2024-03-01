import qrcode
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django_otp import devices_for_user

from .forms import RegisterForm
from .models import Stronghold, Action, Team, Score, Player
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from collections import defaultdict
from django_otp.plugins.otp_totp.models import TOTPDevice
import io

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
        user_actions = Score.objects.filter(user=user.pk)
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

"""
This function links leaderboard url to leaderboard.html file. It also passes dicts that contain sorted users with total points
and groups with total points.

Written by Fedor Morgunov
"""


def auth(request):
    return render(request, 'auth.html')

"""
 This function andles user login authentication.

    Parameters:
    - request: HttpRequest object containing requesting the login user information

Written by Jiadong Cheang
"""


def log_in(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Authenticate the user using username/password
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Check if the user has an OTP device configured
                otp_devices = devices_for_user(user)
                try:
                    device = next(otp_devices)  # Get the first OTP device
                    return redirect('/otplogin')  # Redirect to OTP login page
                except StopIteration:
                    # No OTP device found, proceed with standard login
                    login(request, user)
                    response = redirect('/')
                    response.set_cookie('userID', user.id, max_age=3600)
                    return response
            else:
                # Authentication failed, set error message
                error_message = "Invalid username or password"
        else:
            # Invalid form data, set error message
            error_message = "Invalid username or password"
    else:
        form = AuthenticationForm()
        error_message = ""

    return render(request, 'login.html', {'form': form, 'error_message': error_message})


def otp_login(request):
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        user = request.user  # Assuming the user is already authenticated

        try:
            # Check if the user has an OTP device configured
            otp_devices = devices_for_user(user)
            device = next(otp_devices)
            if device.verify_token(otp_code):
                # OTP code is valid, log in the user
                login(request, user)
                response = redirect('/')
                response.set_cookie('userID', user.id, max_age=3600)
                return response
            else:
                # Invalid OTP code, set error message
                error_message = "Invalid OTP code"
        except TOTPDevice.DoesNotExist:
            # No OTP device found for the user, set error message
            error_message = "OTP authentication is not enabled for your account"
    else:
        error_message = ""

    return render(request, 'login_with_otp.html', {'error_message': error_message})

"""
This function takes the values from the registration form and creates the necessary django auth user and the associated player instance in the database

Written by Jiadong Cheang and Tom Shannon
"""


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


"""
The following function are used for the redeem_points page
The first function redeem_points is used to pass the parameters from the url to the HTML document
The Second function get_building_and_action_names is used to return the building name and action name from the database based on the url parameters via a jquery request from the javascript code
The third function write_to_score_table is used to write the user,action and building to the database base by using the url parameters and the users cookie value via a jquery request from the javascript code

Written by Tom Shannon

"""

def redeem_points(request, buildingID, actionID):
    context = {#extract the values from the url
        'buildingID': buildingID,
        'actionID': actionID,
    }
    return render(request, 'redeem_points.html', context)

def get_building_and_action_names(request, buildingID, actionID):
    try:
        building = Stronghold.objects.get(id=buildingID) #get the values from the database
        action = Action.objects.get(id=actionID)
        
        data = {#asign the values for the json response
            'buildingName': building.building_name,
            'actionName': action.action_name
        }
        return JsonResponse(data)
    except (Stronghold.DoesNotExist, Action.DoesNotExist):
        return JsonResponse({'error': 'Building,Action or User not found'}, status=404)


def write_to_score_table(request):
    if request.method == 'POST':
        try:
            #obtain the values from the post request
            userID = request.POST.get('userID')
            buildingID = request.POST.get('buildingID')
            actionID = request.POST.get('actionID')
            dateTimeEarned = request.POST.get('dateTimeEarned')
            

            # Retrieve the User instance
            user = get_object_or_404(User, pk=userID)
            
            # Retrieve the associated Player,building and action
            player = get_object_or_404(Player, user=user)
            stronghold = get_object_or_404(Stronghold, pk=buildingID)
            action = get_object_or_404(Action, pk=actionID)
            # Create a new Score object and save it to the database
            score = Score(user=player, action_site=stronghold, action_done=action, datetime_earned=dateTimeEarned)
            score.save()

            # Retrieve building name, action name, and points value
            building_name = Stronghold.objects.get(id=buildingID).building_name
            action_name = Action.objects.get(id=actionID).action_name
            points_value = Action.objects.get(id=actionID).points_value

            return JsonResponse({#return the parameters so the dynamic html element can display a confirmation message
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



import qrcode
from django.http import HttpResponse
from django_otp.plugins.otp_totp.models import TOTPDevice

def generate_totp_secret(request):
    # Generate TOTP secret key
    user = request.user
    totp_device = TOTPDevice.objects.create(user=user)
    totp_secret = totp_device.config_url

    # Generate QR code
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(totp_secret)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Return QR code image
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response

