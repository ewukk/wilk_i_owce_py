window.selectPiece = function(row, col, playerRole) {
    // Sprawdź aktualną rolę gracza
    let currentPlayerRole = currentTurn === 'player' ? playerRole : computerRole;

    // Sprawdź, czy kliknięty pionek odpowiada roli gracza
    let selectedPiece = document.querySelector(`.piece[data-row="${row}"][data-col="${col}"]`);
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

        // Pobierz te informacje po zapisaniu
        let selectedPieceRow = sessionStorage.getItem('selectedPieceRow');
        let selectedPieceCol = sessionStorage.getItem('selectedPieceCol');
        console.log('Po pobraniu z sessionStorage:', selectedPieceRow, selectedPieceCol);

        // Ustaw wartości w formularzu
        document.getElementById('selectedRow').value = row;
        document.getElementById('selectedCol').value = col;
        document.getElementById('pieceForm').submit();
    } else {
        console.log('Nie możesz zaznaczyć tego pionka.');
    }
}

function submitMove(row, col) {
    // Ustaw wartości w ukrytych polach formularza moveForm
    document.getElementById('selectedMoveRow').value = row;
    document.getElementById('selectedMoveCol').value = col;

    // Wyślij żądanie POST do /move
    document.getElementById('moveForm').submit();
}
