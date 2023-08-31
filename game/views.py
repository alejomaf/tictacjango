# game/views.from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.contrib.auth import logout,  login, authenticate
from .forms import UserRegistrationForm, LoginForm
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Game, Board, Player
from .serializers import GameSerializer, BoardSerializer
from .services import is_valid_move, update_board, check_winner

import hashlib
import random
import uuid


@login_required(login_url='/login/')
def create_game(request):
    if request.method == "POST":
        token = uuid.uuid4().hex
        player1 = request.user
        new_game = Game.objects.create(token=token, player1=player1)
        return redirect(f"/game/{token}")
    return render(request, "create_game.html")


@login_required(login_url='/login/')
def game_view(request, token):
    game = Game.objects.get(token=token)
    if request.user == game.player1 or request.user == game.player2:
        return render(request, "game.html", {"game": game})
    else:
        return HttpResponseForbidden("No tienes permiso para acceder a esta partida.")


@login_required(login_url='/login/')
def game_history(request):
    player_games = Game.objects.filter(player1=request.user) | Game.objects.filter(player2=request.user)
    return render(request, "game_history.html", {"games": player_games})


@login_required(login_url='/login/')
def home_view(request):
    return render(request, 'home.html')


@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Guardar el usuario en la tabla User
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.save()

            # Crear y guardar un nuevo Player vinculado al User
            player = Player(username=user.username)
            player.save()

            # Autenticar y loguear al usuario
            username = form.cleaned_data.get('username')
            user = authenticate(username=username, password=form.cleaned_data.get('password'))
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        print("Coge el formulario")
        print(form.errors)
        if form.is_valid():
            print("Form is valid")  # Debug line
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            print(f"User {username} password {password}")  # Debug line

            user = authenticate(username=username, password=password)
            print(f"User object: {user}")  # Debug line

            if user is not None:
                login(request, user)

                random_data = str(random.getrandbits(256))
                hash_code = hashlib.sha256(random_data.encode()).hexdigest()
                print(f"Hash code: {hash_code}")  # Debug line
                request.session['hash_code'] = hash_code
                user.hash_code = hash_code
                user.save()

                return redirect('home')
            else:
                print("Authentication failed")  # Debug line
    else:
        print("Form is not valid")
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def some_protected_view(request):
    hash_code = request.session.get('hash_code')
    try:
        user = Player.objects.get(hash_code=hash_code)
    except Player.DoesNotExist:
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    if user:
        return render(request, "some_protected_view.html")
    else:
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")


class GameViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class BoardViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def update(self, request, *args, **kwargs):
        board = self.get_object()
        move = request.data.get('move')
        player = request.data.get('player')

        if is_valid_move(board.state, move):
            new_state = update_board(board.state, move, player)
            board.state = new_state
            board.save()

            winner = check_winner(new_state)
            if winner:
                game = board.game
                game.is_over = True
                game.winner = player
                game.save()

            return Response({"status": "move made", "winner": winner}, status=200)

        return Response({"status": "invalid move"}, status=400)
