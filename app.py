import random
from flask import Flask, render_template, request, session, redirect, url_for
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
    sheep_positions = [{"id": f"sheep{i}", "row": 3, "col": 2 * i} for i in range(4)]

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
        selected_role = request.form['figure']
        session['player_role'] = selected_role
        create_game_instance()
        print(session['player_role'])
        session['computer_role'] = "owca" if selected_role == "wilk" else "wilk"
        session.modified = True
        return redirect('/game?player_role=' + selected_role)
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
    try:
        session['current_turn'] = 'player'
        # Sprawdź role użytkowników
        player_role = session.get('player_role')
        computer_role = session.get('computer_role')
        print(f"DEBUG: Player Role: {player_role}")
        print(f"DEBUG: Computer Role: {computer_role}")
        game_instance = GI[session.get('game_instance')]
        is_game_over, game_result = game_instance.is_game_over()

        if not is_game_over:  #
            print("DEBUG: Tura gracza")  #
            redirect('/move')  # Sprawdzić, czy to jest potrzebne
        else:  #
            winner = game_result  #
            return redirect(url_for('game_over', winner=winner))  #

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
                               BOARD=BOARD, game_instance=session.get('game_instance'), player_role=player_role)
    except KeyError as e:
        # Obsługa błędu KeyError
        print(f"Błąd KeyError: {e}")
        # Przekieruj użytkownika z powrotem do '/hello'
        return redirect(url_for('hello'))


@app.route('/move', methods=['POST'])
def move():
    try:
        print(f"DEBUG: Session contents before /move: {session}")
        game_instance = GI[session.get('game_instance')]
        # Wyświetlenie szachownicy
        for row in board():
            print(' '.join(map(str, row)))

        print('Formularz', request.form)
        # Sprawdź, czy form_type istnieje w żądaniu POST
        form_type = request.form.get('form_type', None)
        sheeps = game_instance.sheep
        wolf = game_instance.wolf
        possible_moves = []

        if form_type == 'pieceForm':
            # Pobierz pozycję zaznaczonego pionka z formularza
            selected_row = int(request.form.get('row'))
            selected_col = int(request.form.get('col'))
            print(f"DEBUG: Selected Row: {selected_row}, Selected Col: {selected_col}")
            print(f"DEBUG: Sheep Positions: {[sheep.get_position() for sheep in sheeps]}")
            print(f"DEBUG: Wolf Position: {wolf.get_position()}")

            # Zaznacz pionka jako wybranego
            for sheep in sheeps:
                sheep.selected = (sheep.row == selected_row and sheep.col == selected_col)
            wolf.selected = (wolf.row == selected_row and wolf.col == selected_col)

            # Określ możliwe ruchy dla zaznaczonego pionka
            possible_moves = get_possible_moves(selected_row, selected_col)
            if not possible_moves:
                # Jeśli brak dostępnych ruchów, przekieruj do strony zakończenia gry
                return redirect(url_for('game_over', winner=session.get('computer_role')))
            print(f"DEBUG: Possible Moves: {possible_moves}")

        elif form_type == 'moveForm':
            # Pobierz pozycję zaznaczonego possible_move z formularza
            selected_move_row = int(request.form.get('moveRow'))
            selected_move_col = int(request.form.get('moveCol'))
            print(f"DEBUG: Selected Move Row: {selected_move_row}, Selected Move Col: {selected_move_col}")

            # Zaktualizuj pozycję pionka gracza w obiekcie game_instance
            player_role = session.get('player_role')
            if player_role == 'wilk':
                game_instance.wolf.set_position(selected_move_row, selected_move_col)
            else:
                # Znajdź odpowiedniego owcę do aktualizacji
                for sheep in game_instance.sheep:
                    if sheep.selected:
                        sheep.set_position(selected_move_row, selected_move_col)

            # Po ruchu gracza sprawdź, czy gra się zakończyła
            is_game_over, game_result = game_instance.is_game_over()

            if not is_game_over:
                # Jeśli gra się nie zakończyła, to przełącz na turę komputera
                game_instance.switch_player()
                session['current_turn'] = 'computer'
                x = handle_computer_move()
                if x == -9:
                    return redirect(url_for('game_over', winner=session.get('player_role')))

                return redirect(url_for('game'))
            else:

                return redirect(url_for('game_over', winner="winner"))

        return render_template('move.html', possible_moves=possible_moves, wolf=wolf, sheeps=sheeps)
    except KeyError as e:
        # Obsługa błędu KeyError
        print(f"Błąd KeyError: {e}")
        # Przekieruj użytkownika z powrotem do '/hello'
        return redirect(url_for('hello'))


@app.route('/game_over', methods=['GET', 'POST'])
def game_over():
    winner = request.args.get('winner')
    return render_template('game_over.html', winner=winner)


@app.route('/handle_computer_move', methods=['GET', 'POST'])
def handle_computer_move():
    session.modified = True
    game_instance = GI[session.get('game_instance')]

    # Pobierz pozycję wilka i owiec oraz rolę komputera
    wolf_position = game_instance.get_wolf().get_position()
    sheeps = game_instance.get_sheep()
    sheep_positions = [sheep.get_position() for sheep in sheeps]
    computer_role = session.get('computer_role')

    # Przekaż te informacje do funkcji obsługującej ruch komputera
    x = get_computer_move(wolf_position, sheep_positions)
    # if x == (None, -9):
    # Jeśli pierwsza wybrana owca nie miała dostępnych ruchów, spróbuj wybrać inną owcę
    # for i, sheep_position in enumerate(sheep_positions):
    # moves_for_sheep = get_possible_moves(*sheep_position)
    # if moves_for_sheep:
    # x = (i, random.choice(moves_for_sheep))
    # print(f"DEBUG: Chosen move for sheep {i}: {x}")
    # break

    if x == (None, -9):
        # Jeśli żadna z owiec nie miała dostępnych ruchów, zakończ ruch komputera
        return -9
    sheepIndex, new_position = x
    print('Sheep Index:', sheepIndex)
    print('New position:', new_position)

    # Sprawdź, czy nowa pozycja różni się od obecnej
    if new_position != wolf_position and new_position not in sheep_positions:
        # Zaktualizuj current_position na nową pozycję
        if computer_role == "wilk":
            game_instance.wolf.set_position(*new_position)
        else:
            chosen_sheep = sheeps[sheepIndex]
            chosen_sheep.set_position(*new_position)

        session['current_turn'] = 'player'
        session.modified = True

    return new_position


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

    possible_moves = [
        (row, col) for row, col in possible_moves if
        is_position_within_board((row, col)) and not is_occupied_by_other_piece((row, col))
    ]

    return possible_moves


def get_computer_move(wolf_position, sheep_positions):
    global move_mapping
    computer_possible_moves = []
    game_instance = GI[session.get('game_instance')]
    computer_role = session.get('computer_role')
    print("DEBUG: Pobierz Ruch Komputera - Start")

    # Sprawdź rolę komputera
    if computer_role == "wilk":
        move_mapping = {
            "DIAGONAL_UP_LEFT": "DIAGONAL_UP_LEFT",
            "DIAGONAL_UP_RIGHT": "DIAGONAL_UP_RIGHT",
            "DIAGONAL_DOWN_LEFT": "DIAGONAL_DOWN_LEFT",
            "DIAGONAL_DOWN_RIGHT": "DIAGONAL_DOWN_RIGHT",
        }
        current_position = game_instance.get_wolf().get_position()
        computer_possible_moves = get_possible_moves(*wolf_position)
        print('Computer possible moves for wolf: ', computer_possible_moves)

        # Wybierz jeden ruch
        chosen_move = random.choice(list(move_mapping.values()))
        print(f"DEBUG: Wybrany ruch komputera: {chosen_move}")
        new_position = calculate_new_position(current_position, chosen_move, computer_role)

        # Sprawdź, czy nowa pozycja jest dostępna (nie zajmuje jej inny pionek)
        att = 0
        while is_occupied_by_other_piece(new_position):
            chosen_move = random.choice(list(move_mapping.values()))
            new_position = calculate_new_position(current_position, chosen_move, computer_role, att)
            print(f"DEBUG: Nowa pozycja pionka: {new_position}")
            if new_position == -9:
                return None, -9
            att += 1

        print("DEBUG: Pobierz Ruch Komputera - Koniec")

        return None, new_position

    elif computer_role == "owca":
        move_mapping = {
            "DIAGONAL_UP_LEFT": "DIAGONAL_UP_LEFT",
            "DIAGONAL_UP_RIGHT": "DIAGONAL_UP_RIGHT",
        }
        for i, sheep_position in enumerate(sheep_positions):
            moves_for_sheep = get_possible_moves(*sheep_position)
            moves_for_sheep = [(r, c) for r, c in moves_for_sheep if r < sheep_position[0]]
            computer_possible_moves.extend([(i, move) for move in moves_for_sheep])

        print('Computer possible moves for sheeps: ', computer_possible_moves)

        # Znajdź owcę, która ma dostępne ruchy
        if not computer_possible_moves:
            # Jeśli brak dostępnych ruchów dla owiec, zakończ ruch komputera
            print("DEBUG: Żadna z owiec nie ma dostępnego ruchu.")
            return None, -9

        # Wybierz losowy ruch spośród dostępnych ruchów dla owiec
        chosen_index, chosen_move = random.choice(computer_possible_moves)
        chosen_sheep = game_instance.get_sheep()[chosen_index]
        print(f"DEBUG: Wybrana owca: {chosen_sheep.get_index()}")
        new_position = chosen_move
        print(f"DEBUG: Wybrana ruch komputera: {chosen_move}")

        # Sprawdź, czy nowa pozycja jest dostępna (nie zajmuje jej inny pionek)
        att = 0
        while new_position == -9 or is_occupied_by_other_piece(new_position):
            # Jeśli nowa pozycja jest zajęta, wybierz inny ruch
            chosen_index, chosen_move = random.choice(computer_possible_moves)
            new_position = calculate_new_position(chosen_sheep.get_position(), chosen_move, computer_role, att)
            if new_position == -9:
                return None, -9
            att += 1

        print(f"DEBUG: Nowa pozycja pionka: {new_position}")

        print("DEBUG: Pobierz Ruch Komputera - Koniec")
        return chosen_sheep.get_index(), new_position


def calculate_new_position(current_position, move, role, attempts=None):
    # Metoda do obliczania nowej pozycji na podstawie aktualnej pozycji, ruchu i roli
    max_attempts = 10
    row, col = current_position
    print(f"DEBUG: Obliczanie nowej pozycji. Aktualna pozycja: {current_position}")
    if attempts is None:
        attempts = 0

    print('matt:', attempts)
    if attempts < max_attempts:
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
            print('Attemps: ', attempts)
            print(f"Nowa pozycja {new_position} wykracza poza szachownicę. Wybieranie nowej pozycji.")
            return calculate_new_position(current_position, "RANDOM_MOVE", role, attempts=attempts + 1)
    else:
        print(f"Nie udało się znaleźć dostępnej pozycji po {max_attempts} próbach. Przekierowanie do /game_over.")
        return -9


def is_position_within_board(position):
    row, col = position
    # Sprawdź, czy indeksy wiersza i kolumny są w granicach szachownicy
    if 0 <= row < len(BOARD) and 0 <= col < len(BOARD[0]):
        return True
    else:
        return False


def is_occupied_by_other_piece(position):
    x = position
    if x == -9:
        return False
    row, col = x

    game_instance = GI[session.get('game_instance')]
    wolf = game_instance.wolf
    sheeps = [sheep.get_position() for sheep in game_instance.sheep]

    # Sprawdź, czy pozycja mieści się w zakresie planszy
    if 0 <= row < len(BOARD) and 0 <= col < len(BOARD[0]):
        # Sprawdź, czy na danej pozycji znajduje się owca
        if (row, col) in sheeps:
            return True

        # Sprawdź, czy na danej pozycji znajduje się wilk
        wolf_row, wolf_col = wolf.get_position()
        if wolf_row == row and wolf_col == col:
            return True

    # Jeśli nie ma owcy ani wilka na danej pozycji, to nie jest zajęte przez inny pionek
    return False


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12106, debug=True)
