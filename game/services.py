from game.models import Board, Game, Player


def is_valid_move(board_state, move):
    return board_state[move] == '-'


def update_board(board_state, move, player):
    if is_valid_move(board_state, move):
        new_state = board_state[:move] + player + board_state[move + 1:]
        return new_state
    return None


def check_winner(board_state):
    winning_combinations = [(0, 1, 2), (3, 4, 5), (6, 7, 8),  # filas
                            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columnas
                            (0, 4, 8), (2, 4, 6)]  # diagonales

    for a, b, c in winning_combinations:
        if board_state[a] == board_state[b] == board_state[c] and board_state[a] != '-':
            return board_state[a]
    return None


def play_move(game_id, move, player):
    game = Game.objects.get(id=game_id)
    board = Board.objects.get(game=game)

    if is_valid_move(board.state, move):
        new_state = update_board(board.state, move, player)
        board.state = new_state
        board.save()

        winner = check_winner(new_state)
        if winner:
            game.is_over = True
            game.winner = player
            game.save()

        return True, winner

    return False, None
