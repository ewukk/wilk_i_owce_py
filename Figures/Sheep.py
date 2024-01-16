class Sheep:
    def __init__(self, row, col, index):
        self.row = row
        self.col = col
        self.index = index

    def get_position(self):
        return self.row, self.col

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_index(self):
        return self.index

