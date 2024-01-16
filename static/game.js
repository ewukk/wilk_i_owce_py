window.selectPiece = function(row, col, playerRole) {
    // Sprawdź aktualną rolę gracza
    var currentPlayerRole = currentTurn === 'player' ? playerRole : computerRole;

    // Sprawdź, czy kliknięty pionek odpowiada roli gracza
    var selectedPiece = document.querySelector(`.piece[data-row="${row}"][data-col="${col}"]`);
    if (selectedPiece && selectedPiece.getAttribute("data-role") === currentPlayerRole) {
        // Usuń zaznaczenie dla wszystkich pionków
        document.querySelectorAll('.piece').forEach(piece => {
            piece.classList.remove('user-selected-piece');
            piece.isSelected = false;
        });

        // Zaznacz wybrany pionek
        selectedPiece.classList.add('user-selected-piece');
        selectedPiece.isSelected = true;

        // Zapisz informacje o zaznaczonym pionku w sessionStorage
        sessionStorage.setItem('selectedPieceRow', row);
        sessionStorage.setItem('selectedPieceCol', col);

        // Przenieś przekierowanie do /move tutaj
        console.log('Zaznaczony pionek w /game:', row, col);
        console.log('Po dodaniu klasy:', selectedPiece.classList);

        // Pobierz te informacje po zapisaniu
        var selectedPieceRow = sessionStorage.getItem('selectedPieceRow');
        var selectedPieceCol = sessionStorage.getItem('selectedPieceCol');
        console.log('Po pobraniu z sessionStorage:', selectedPieceRow, selectedPieceCol);

        // Ustaw wartości w formularzu
        document.getElementById('selectedRow').value = row;
        document.getElementById('selectedCol').value = col;
        document.getElementById('pieceForm').submit();
    } else {
        console.log('Nie możesz zaznaczyć tego pionka.');
    }
}



// Funkcja do obsługi kliknięcia w możliwe pole ruchu
function submitMove(row, col) {
    // Ustaw wartości w formularzu
    document.getElementById('selectedRow').value = row;
    document.getElementById('selectedCol').value = col;

    // Wyślij żądanie POST do /game
    document.getElementById('moveForm').submit();
}

