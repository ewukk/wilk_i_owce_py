from Players.Player import SheepPlayer, WolfPlayer
from Figures.Sheep import Sheep
from Figures.Wolf import Wolf


def create_player(role):
    if role is None or role == 'owca':
        return SheepPlayer()
    elif role == 'wilk':
        return WolfPlayer()
    else:
        raise ValueError(f"Nieznana rola: {role}")


def board():
    BOARD = [
        [0, 1, 2, 3, 4, 5, 6, 7],
        [1, 1, 2, 3, 4, 5, 6, 7],
        [2, 1, 2, 3, 4, 5, 6, 7],
        [3, 1, 2, 3, 4, 5, 6, 7],
        [4, 1, 2, 3, 4, 5, 6, 7],
        [5, 1, 2, 3, 4, 5, 6, 7],
        [6, 1, 2, 3, 4, 5, 6, 7],
        [7, 1, 2, 3, 4, 5, 6, 7]
    ]
    return BOARD


class Game:
    def __init__(self, player, computer_player, session):
        self.player = player
        self.computer_player = computer_player
        self.session = session
        self.players = [self.player, self.computer_player]
        self.current_player = self.player
        self.last_move = None
        self.player_role = None
        self.user_move_completed = False
        self.move_history = {"owca": [], "wilk": []}
        self.wolf = Wolf(0, 3)
        self.sheep = [Sheep(3, 0, 0), Sheep(3, 2, 1), Sheep(3, 4, 2), Sheep(3, 6, 3)]

    def get_wolf(self):
        return self.wolf

    def get_sheep(self):
        return self.sheep

    def set_player_role(self, role):
        if role == 'owca':
            self.player.set_player_role(role)
            self.computer_player.set_player_role('wilk')
        elif role == 'wilk':
            self.player.set_player_role(role)
            self.computer_player.set_player_role('owca')
        else:
            raise ValueError(f"Nieznana rola: {role}")

    def switch_player(self):
        self.current_player = (
            self.player if self.current_player == self.computer_player else self.computer_player
        )

    def is_player_turn(self):
        print(f"DEBUG: Checking if it's player's turn. Current player: {self.current_player.get_role()}")
        return self.current_player == self.player

    def is_game_over(self):
        if self.is_wolf_winner():
            print("DEBUG: Wolf wins condition met")
            return True, self.current_player.get_role()
        elif self.is_sheep_winner():
            print("DEBUG: Sheep wins condition met")
            return True, self.current_player.get_role()

        return False, "Gra trwa."

    def is_wolf_winner(self):
        wolf_row, wolf_col = self.wolf.get_position()

        # Sprawdź, czy wszystkie owce są w rzędzie o indeksie 0
        all_sheep_in_top_row = all(sheep.get_position()[0] == 0 for sheep in self.sheep)

        # Zwycięstwo wilka, jeśli znajduje się w rzędzie o indeksie 7 i wszystkie owce są w rzędzie o indeksie 0
        wolf_winner = wolf_row == 7 or all_sheep_in_top_row

        return wolf_winner

    def is_sheep_winner(self):
        row, col = self.wolf.get_position()
        sheep_winner = all(
            sheep.get_position() == (row - 1, col) or sheep.get_position() == (row + 1, col)
            for sheep in self.sheep)

        return sheep_winner
