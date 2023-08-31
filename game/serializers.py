from rest_framework import serializers
from .models import Board, Game, Player


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'state']


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'username']


class GameSerializer(serializers.ModelSerializer):
    player1 = PlayerSerializer()
    player2 = PlayerSerializer()
    board = BoardSerializer()
    current_turn = PlayerSerializer()
    winner = PlayerSerializer()

    class Meta:
        model = Game
        fields = ['id', 'token', 'player1', 'player2', 'board', 'current_turn', 'is_over', 'winner']
