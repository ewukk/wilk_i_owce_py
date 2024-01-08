class Player:
    def __init__(self):
        self.role = None
        self.position = None
        self.wolf = None
        self.sheep = None

    def get_role(self):
        return self.role

    def get_wolf(self):
        return self.wolf

    def get_sheep(self):
        return self.sheep

    def set_player_role(self, role):
        self.role = role


class SheepPlayer(Player):
    def get_wolf_position(self):
        return self.get_wolf().get_position()

    def get_sheep_positions(self):
        return [sheep.get_position() for sheep in self.get_sheep()]

    def set_player_role(self, role):
        super().set_player_role(role)


class WolfPlayer(Player):
    def get_wolf_position(self):
        return self.get_wolf().get_position()

    def get_sheep_positions(self):
        return [sheep.get_position() for sheep in self.get_sheep()]

    def set_player_role(self, role):
        super().set_player_role(role)
