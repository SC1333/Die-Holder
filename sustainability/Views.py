from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetForm
from django.contrib.auth import login, authenticate
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib import messages
from .forms import RegisterForm, PasswordResetForm
from .models import Stronghold, Action, Team, Score, Player
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
    
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Check if the email exists in the User database
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                # Generate a password reset token and send email to user
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token}))
                email_subject = 'Password Reset Request'
                email_message = f'Hi {user.username},\n\nTo reset your password, click the following link:\n\n{reset_url}'
                send_mail(email_subject, email_message, 'your_email@gmail.com', [email])
                messages.success(request, 'Password reset email has been sent.')
                return redirect('password_reset_done')
            else:
                messages.error(request, 'Email does not exist.')
    else:
        form = PasswordResetForm()

    return render(request, 'password_reset_request.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    try:
        # Decode the user ID from base64
        uid = force_text(urlsafe_base64_decode(uidb64))
        # Get the user object corresponding to the user ID
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Check if the user exists and the token is valid
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                # Save the new password
                form.save()
                messages.success(request, 'Your password has been reset. You can now log in with your new password.')
                return redirect('login')  # Redirect to login page after successful password reset
        else:
            # Render the password reset confirmation form
            form = SetPasswordForm(user)
        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        # Display an error message for invalid token or user
        messages.error(request, 'The password reset link is no longer valid. Please request a new one.')
        return redirect('password_reset')


def password_reset_done(request):
    return render(request, 'password_reset_done.html')


def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')
    

"""
 This function andles user login authentication.

    Parameters:
    - request: HttpRequest object containing requesting the login user information

Written by Jiadong Cheang
"""


def log_in(request):
    if request.method == 'POST':
        # Create an AuthenticationForm instance with the POST data
        form = AuthenticationForm(request, request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Authenticate the user
            user = authenticate(request, username=username, password=password)
            
            # If user is authenticated, log them in
            if user is not None:
                login(request, user)
                
                # Set a cookie for the username
                response = redirect('/')
                response.set_cookie('userID', user.id, max_age=3600)
                
                return response
            else:
                # If authentication fails, set an error message
                error_message = "Invalid username or password"
        else:
            error_message = form.error_messages['invalid_login']
    else:
        form = AuthenticationForm()
        error_message = ""

    # Render the login.html template with the form and error message
    return render(request, 'login.html', {'form': form, 'error_message': error_message})



"""
This function takes the values from the registration form and creates the necessary django auth user and the associated player instance in the database

Written by Jiadong Cheang and Tom Shannon
"""


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            is_username_taken = User.objects.filter(username=form.cleaned_data['username']).exists()
            is_email_taken = User.objects.filter(email=form.cleaned_data['email']).exists()
            if is_username_taken or is_email_taken:
                error_message = 'Username already taken' if is_username_taken else 'Email already taken'
                return render(request, 'register.html', {'form': form, 'error_message': error_message})
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
