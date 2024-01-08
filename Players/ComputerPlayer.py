from Players.Player import Player


class ComputerPlayer(Player):
    def __init__(self):
        super().__init__()

    def get_role(self):
        return self.role

    def set_player_role(self, role):
        self.role = role
