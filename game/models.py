from django.db import models


class Player(models.Model):
    username = models.CharField(max_length=50, unique=True)
    score = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)


class Board(models.Model):
    state = models.CharField(max_length=9, default="---------")


class Game(models.Model):
    token = models.CharField(max_length=50, unique=True)
    player1 = models.ForeignKey(Player, related_name='games_as_player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(Player, related_name='games_as_player2', on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    current_turn = models.ForeignKey(Player, related_name='games_as_current_turn', on_delete=models.CASCADE)
    is_over = models.BooleanField(default=False)
    winner = models.ForeignKey(Player, related_name='games_as_winner', on_delete=models.CASCADE, null=True)


# python manage.py makemigrations
# python manage.py migrate
