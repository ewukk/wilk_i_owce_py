import random
from flask import Flask, render_template, request, session, redirect, url_for
from Figures.Wolf import Wolf
from Players.ComputerPlayer import ComputerPlayer
from game import create_player, Game, board

app = Flask(__name__)
app.secret_key = 'wilk_i_owce'

GI = {}


def create_game_instance():
    player_role = session.get('player_role')
    player = create_player(player_role)
    computer_player = ComputerPlayer()
    game_instance = Game(player, computer_player, session)
    game_instance.set_player_role(player_role)
    klucz = 1
    GI[klucz] = game_instance
    session['game_instance'] = klucz
    print('****', session)


# Funkcja do generowania początkowych pozycji pionków
def generate_initial_positions():
    # Początkowe pozycje wilka i owiec
    wolf_position = {"id": "wolf", "row": 0, "col": 0}
    sheep_positions = [{"id": f"sheep{i}", "row": 7, "col": 2 * i} for i in range(4)]

    # Zwróć listę początkowych pozycji pionków
    return [wolf_position] + sheep_positions


data = {
    "pieces": generate_initial_positions()
}

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


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/')
def hello():
    return render_template('hello.html')


@app.route('/choose_figure', methods=['GET', 'POST'])
def choose_figure():
    if request.method == 'POST':
        # Utwórz nową instancję gry dla sesji gracza
        create_game_instance()
        selected_role = request.form['figure']
        session['player_role'] = selected_role
        session['computer_role'] = "owca" if selected_role == "wilk" else "wilk"
        session.modified = True
        return redirect('/game')
    return render_template('choose_figure.html', player_role=session.get('player_role'))


@app.route('/game', methods=['GET', 'POST'])
def game():
    result = ""
    computer_result = ""

    # Wyświetlenie szachownicy
    for row in board():
        print(' '.join(map(str, row)))

    # Sprawdź, czy rola gracza jest już ustawiona
    if 'player_role' not in session:
        player_role = request.args.get('player_role')
        if player_role:
            session['player_role'] = player_role
        else:
            return redirect('/choose_figure')

    session['current_turn'] = 'player'
    # Sprawdź role użytkowników
    player_role = session.get('player_role')
    computer_role = session.get('computer_role')
    print(f"DEBUG: Player Role: {player_role}")
    print(f"DEBUG: Computer Role: {computer_role}")
    game_instance = GI[session.get('game_instance')]
    is_game_over, game_result = game_instance.is_game_over()

    if not is_game_over:
        if request.method == 'POST':
            if game_instance.is_player_turn():
                # Logika dla tury gracza
                print("DEBUG: Tura gracza")
                handle_player_move()

    sheeps = game_instance.sheep
    wolf = game_instance.wolf
    print('=========', game_instance.wolf)
    sheep_positions = [sheep.get_position() for sheep in sheeps]
    initialSheepPositions = [sheep.get_position() for sheep in sheeps]

    return render_template('game.html', sheeps=sheeps, wolf=wolf, result=result,
                           computer_result=computer_result, sheep_positions=sheep_positions,
                           initialSheepPositions=initialSheepPositions,
                           move_history=game_instance.move_history,
                           is_game_over=is_game_over, current_turn=session.get('current_turn'),
                           BOARD=BOARD, game_instance=session.get('game_instance'))


@app.route('/move', methods=['GET'])
# @app.route('/move/<row:int>/<col:int>', methods=['GET'])
def move(selected_row=None, selected_col=None):
    print(f"DEBUG: Session contents before /move: {session}")
    game_instance = session['game_instance']
    # Wyświetlenie szachownicy
    for row in board():
        print(' '.join(map(str, row)))

    # Pobierz pozycję zaznaczonego pionka z formularza
    selected_row = int(request.form.get('row'))
    selected_col = int(request.form.get('col'))

    sheeps = game_instance.sheep
    wolf = game_instance.wolf

    # Zaznacz pionka jako wybranego
    for sheep in sheeps:
        sheep.selected = (sheep.row == selected_row and sheep.col == selected_col)
    wolf.selected = (wolf.row == selected_row and wolf.col == selected_col)

    # Określ możliwe ruchy dla zaznaczonego pionka
    possible_moves = get_possible_moves(selected_row, selected_col)

    if request.method == 'POST':

        # Po ruchu gracza sprawdź, czy gra się zakończyła
        is_game_over, game_result = game_instance.is_game_over()

        if not is_game_over:
            # Jeśli gra się nie zakończyła, to przełącz na turę komputera
            game_instance.switch_player()
            session['current_turn'] = 'computer'
            handle_computer_move()

        return redirect(url_for('game'))

    return render_template('move.html', possible_moves=possible_moves, wolf=wolf, sheeps=sheeps)


@app.route('/handle_computer_move', methods=['POST'])
def handle_computer_move():
    session.modified = True
    if 'game_instance' in session:
        game_instance = session.get('game_instance')
        # Pobierz pozycję wilka i owiec oraz rolę komputera
        wolf_position = game_instance.get_wolf().get_position()
        sheeps = game_instance.get_sheep()
        sheep_positions = [sheep.get_position() for sheep in sheeps]
        computer_role = session.get('computer_role')
        print('=====')

        # Przekaż te informacje do funkcji obsługującej ruch komputera
        new_position = get_computer_move(wolf_position, sheep_positions)

        print('33333')
        # Zaktualizuj current_position na nową pozycję
        if computer_role == "wilk":
            game_instance.wolf.set_position(*new_position)
            print('666')
            print('*****', game_instance.wolf)
        else:
            print('----')
            chosen_sheep = sheeps[new_position.get('sheepIndex')]
            chosen_sheep.set_position(*new_position)

        print('22222')

        session['current_turn'] = 'player'
        session.modified = True
        print('===========')

        return new_position
    else:
        # Obsługa, gdy game_instance nie istnieje w sesji
        return "Błąd: Brak instancji gry w sesji."


def handle_player_move():
    if 'game_instance' in session:
        user_move = redirect('/move')
        print("DEBUG: Handling player move")
        session.modified = True
        return user_move
    else:
        # Obsługa, gdy game_instance nie istnieje w sesji
        return "Błąd: Brak instancji gry w sesji."


def get_possible_moves(row, col):
    possible_moves = []
    player_role = session.get('player_role')

    if player_role == 'wilk':
        # Logika dla ruchu wilka (na ukos)
        possible_moves = [
            (row - 1, col - 1), (row - 1, col + 1),
            (row + 1, col - 1), (row + 1, col + 1)
        ]
    elif player_role == 'owca':
        # Logika dla ruchu owcy (do przodu na ukos)
        possible_moves = [(row - 1, col - 1), (row - 1, col + 1)]

    # Filtruj możliwe ruchy, aby nie wyjść poza szachownicę
    possible_moves = [(row, col) for row, col in possible_moves if is_position_within_board((row, col))]

    # Dodaj logikę, aby nie zachodzić na inne pionki
    possible_moves = [(row, col) for row, col in possible_moves if not is_occupied_by_other_piece((row, col))]

    return possible_moves


def is_position_within_board(position):
    row, col = position

    # Sprawdź, czy indeksy wiersza i kolumny są w granicach szachownicy
    if 0 <= row < len(BOARD) and 0 <= col < len(BOARD[0]):
        return True
    else:
        return False


def is_occupied_by_other_piece(position):
    row, col = position
    if 'game_instance' in session:
        game_instance = session.get('game_instance')
        wolf = game_instance.wolf.get_position()
        sheeps = [sheep.get_position() for sheep in game_instance.sheep]

        # Sprawdź, czy pozycja mieści się w zakresie planszy
        if 0 <= row < len(BOARD) and 0 <= col < len(BOARD[0]):
            # Sprawdź, czy na danej pozycji znajduje się owca
            for sheep in sheeps:
                sheep_row, sheep_col = sheep.get_position()
                if 0 <= sheep_row < len(BOARD) and 0 <= sheep_col < len(BOARD[0]):
                    if sheep_row == row and sheep_col == col:
                        return True

            # Sprawdź, czy na danej pozycji znajduje się wilk
            wolf_row, wolf_col = wolf.get_position()
            if 0 <= wolf_row < len(BOARD) and 0 <= wolf_col < len(BOARD[0]):
                if wolf_row == row and wolf_col == col:
                    return True

        # Jeśli nie ma owcy ani wilka na danej pozycji, to nie jest zajęte przez inny pionek
        return False
    else:
        # Obsługa, gdy game_instance nie istnieje w sesji
        return "Błąd: Brak instancji gry w sesji."


def get_computer_move(wolf_position, sheep_positions):
    global move_mapping

    if 'game_instance' in session:
        game_instance = session.get('game_instance')
        print("DEBUG: Pobierz Ruch Komputera - Start")

        computer_role = session.get('computer_role')

        # Sprawdź rolę komputera
        if computer_role == "wilk":
            move_mapping = {
                "DIAGONAL_UP_LEFT": "DIAGONAL_UP_LEFT",
                "DIAGONAL_UP_RIGHT": "DIAGONAL_UP_RIGHT",
                "DIAGONAL_DOWN_LEFT": "DIAGONAL_DOWN_LEFT",
                "DIAGONAL_DOWN_RIGHT": "DIAGONAL_DOWN_RIGHT",
            }
            current_position = game_instance.get_wolf().get_position()
            # Wybierz jeden ruch
            chosen_move = random.choice(list(move_mapping.values()))
            new_position = calculate_new_position(current_position, chosen_move, computer_role)

            print(f"DEBUG: Wybrany ruch komputera: {chosen_move}")
            print(f"DEBUG: Nowa pozycja pionka: {new_position}")
            print("DEBUG: Pobierz Ruch Komputera - Koniec")

            return new_position

        elif computer_role == "owca":
            move_mapping = {
                "DIAGONAL_UP_LEFT": "DIAGONAL_UP_LEFT",
                "DIAGONAL_UP_RIGHT": "DIAGONAL_UP_RIGHT",
            }
            # Wybierz losową owcę
            chosen_sheep = random.choice(game_instance.get_sheep())
            sheepIndex = chosen_sheep.get_index()
            current_position = chosen_sheep.get_position()
            print(f"DEBUG: Wybrana owca: {sheepIndex}")

            # Wybierz jeden ruch
            chosen_move = random.choice(list(move_mapping.values()))
            print(f"DEBUG: Wybrany ruch komputera: {chosen_move}")

            # Oblicz ruch na podstawie pozycji wybranej owcy
            new_position = calculate_new_position(current_position, chosen_move, computer_role)
            print(f"DEBUG: Nowa pozycja pionka: {new_position}")

            print("DEBUG: Pobierz Ruch Komputera - Koniec")

            return new_position
        else:
            # Obsługa, gdy game_instance nie istnieje w sesji
            return "Błąd: Brak instancji gry w sesji."


def calculate_new_position(current_position, move, role):
    # Metoda do obliczania nowej pozycji na podstawie aktualnej pozycji, ruchu i roli
    row, col = current_position
    print(f"DEBUG: Obliczanie nowej pozycji. Aktualna pozycja: {current_position}")

    if role == 'wilk':
        # Logika dla ruchu wilka
        if move == 'DIAGONAL_UP_LEFT':
            new_position = row - 1, col - 1
        elif move == 'DIAGONAL_UP_RIGHT':
            new_position = row - 1, col + 1
        elif move == 'DIAGONAL_DOWN_LEFT':
            new_position = row + 1, col - 1
        elif move == 'DIAGONAL_DOWN_RIGHT':
            new_position = row + 1, col + 1
        else:
            new_position = row, col
    elif role == 'owca':
        # Logika dla ruchu owcy
        if move == 'DIAGONAL_UP_LEFT':
            new_position = row - 1, col - 1
        elif move == 'DIAGONAL_UP_RIGHT':
            new_position = row - 1, col + 1
        else:
            new_position = row, col
    else:
        # Logika dla innej roli (możesz dostosować do własnych potrzeb)
        new_position = row, col

    # Sprawdź, czy nowa pozycja wykracza poza szachownicę
    if is_position_within_board(new_position):
        return new_position
    else:
        print(f"Nowa pozycja {new_position} wykracza poza szachownicę. Wybieranie nowej pozycji.")

        return calculate_new_position(current_position, "RANDOM_MOVE", role)


if __name__ == '__main__':
    app.run(debug=True)
