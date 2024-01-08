from Players.Player import Player, SheepPlayer, WolfPlayer
from Players.ComputerPlayer import ComputerPlayer
from Figures.Sheep import Sheep
from Figures.Wolf import Wolf


def create_game_instance(session):
    player = Player()
    computer_player = ComputerPlayer()
    return Game(player, computer_player, session)


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

    for i in range(8):
        for j in range(8):
            if i == 0 and j == 3:
                BOARD[i][j] = 2  # Wilk
            elif i == 7 and j in [0, 2, 4, 6]:
                BOARD[i][j] = 1  # Owca

    return BOARD


def is_position_within_board(position, BOARD_SIZE=8, TILE_SIZE=50):
    max_coordinate = BOARD_SIZE * TILE_SIZE
    return 0 <= position[0] < max_coordinate and 0 <= position[1] < max_coordinate


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
        self.wolf = Wolf(0, 0)
        self.sheep = [Sheep(2 * i, 7, j) for i in range(1, 8, 2) for j in range(4)]

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

    def get_move_history(self):
        # Ustaw domyślną rolę, jeśli player_role nie jest ustawiona
        print(f"Komputer widzi grę jako {self.current_player.get_role()}")
        player_role = self.current_player.get_player_role() if self.current_player.get_player_role() is not None \
            else 'owca'

        # Uwzględnij rolę komputera
        if isinstance(self.current_player, ComputerPlayer):
            player_role = self.current_player.get_role()

        return self.move_history.get(player_role, [])

    def is_game_over(self):
        if self.is_wolf_winner():
            print("DEBUG: Wolf wins condition met")
            return True, "Wilk wygrywa!"
        elif self.is_sheep_winner():
            print("DEBUG: Sheep wins condition met")
            return True, "Owce wygrywają!"
        elif self.is_blocked():
            print("DEBUG: Blocked condition met")
            return True, "Owce zablokowały wilka. Koniec gry!"

        return False, "Gra trwa."

    def is_wolf_winner(self):
        row, col = self.wolf.get_position()
        wolf_winner = col == 7

        return wolf_winner

    def is_sheep_winner(self):
        sheep_winner = all(sheep.get_position()[1] == 0 for sheep in self.sheep)

        return sheep_winner

    def is_blocked(self):
        row, col = self.wolf.get_position()
        blocked_condition = all(
            sheep.get_position() == (row - 1, col) or sheep.get_position() == (row + 1, col)
            for sheep in self.sheep)

        return blocked_condition
