import {Chessboard, COLOR, INPUT_EVENT_TYPE} from './node_modules/cm-chessboard/src/Chessboard.js';
import {Markers} from './node_modules/cm-chessboard/src/extensions/markers/Markers.js';
import {PROMOTION_DIALOG_RESULT_TYPE, PromotionDialog} from "./node_modules/cm-chessboard/src/extensions/promotion-dialog/PromotionDialog.js"
import {Accessibility} from "./node_modules/cm-chessboard/src/extensions/accessibility/Accessibility.js";
import {Chess} from './chess.js';


function show_alert(message, type) {
    const alertPlaceholder = document.getElementById('alertPlaceholder');
    const wrapper = document.createElement('div');
    wrapper.innerHTML = [
        `<div class="alert alert-${type} alert-dismissible text-center" role="alert">`,
        `   <div>"${message}"</div>`,
        '   <button type="button" class="btn btn-primary mt-2" data-bs-dismiss="alert" aria-label="Close" onclick="location.reload();">Next</button>',
        '</div>'
    ].join('');

    alertPlaceholder.append(wrapper);
}


function get_puzzle() {
    fetch('/get_puzzle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({"names": []}),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            puzzle_start_time = Date.now();
            puzzle = data;
            if (data == null || data == "" || data == {}) {
                show_alert("No more puzzles available!", "info");
                return;
            }
            setup_board(data);
        });
}

get_puzzle();
let chess = new Chess();
let puzzle = null;
let puzzle_start_time = null;
let nth_move = 1;


let board = new Chessboard(document.getElementById('board'), {
    assetsUrl: "./node_modules/cm-chessboard/assets/",
    style: {pieces: {file: "pieces/staunty.svg"}, animationDuration: 300},
    extensions: [
        {class: Markers},
        {class: PromotionDialog},
        {class: Accessibility, props: {visuallyHidden: true}}
    ]
});

function setup_board(puzzle) {
    chess.load(puzzle.fen);
    board.setPosition(puzzle.fen);
    board.setOrientation(puzzle.orientation == "white" ? COLOR.white : COLOR.black);
    document.getElementById("title").innerHTML = puzzle.category;
    document.getElementById("hint_1").innerHTML = puzzle.hint_1;
    document.getElementById("hint_2").innerHTML = puzzle.hint_2;
    
    setTimeout(() => {
        chess.move(puzzle.pre_move);
        board.setPosition(chess.fen(), true);
    }, 500);    
}

function input_handler(event) {
    console.log(event);
    switch (event.type) {
        case INPUT_EVENT_TYPE.moveInputStarted:
            return true;

        case INPUT_EVENT_TYPE.validateMoveInput:
            const move = {from: event.squareFrom, to: event.squareTo, promotion: event.promotion};
            const move_result = chess.move(move);

            if (move_result) {
                event.chessboard.state.moveInputProcess.then(() => {
                    event.chessboard.setPosition(chess.fen(), true).then(() => {
                        update_and_validate(event, puzzle);
                    });
                });
            }
            else {
                let possible_moves = chess.moves({square: event.squareFrom, verbose: true});
                for (const possible_move of possible_moves) {
                    if (possible_move.promotion && possible_move.to === event.squareTo) {
                        event.chessboard.showPromotionDialog(event.squareTo, puzzle.orientation, (result) => {
                            console.log("promotion result: ", result);
                            if (result.type === PROMOTION_DIALOG_RESULT_TYPE.pieceSelected) {
                                chess.move({from: event.squareFrom, to: event.squareTo, promotion: result.piece.charAt(1)});
                                event.chessboard.setPosition(chess.fen(), true).then(() => {
                                    update_and_validate(event, puzzle);
                                });
                            }
                            else {
                                event.chessboard.enableMoveInput(input_handler, puzzle.orientation);
                                event.chessboard.setPosition(chess.fen(), true).then(() => {
                                    update_and_validate(event, puzzle);
                                });
                            }
                        });
                        return true;
                    }
                }
            }
            return !!move_result;

        case INPUT_EVENT_TYPE.moveInputFinished:
            event.chessboard.disableMoveInput();
            event.chessboard.setPosition(chess.fen(), false);
            if (!event.legalMove) {
                show_alert("Illegal move!", "danger");
            }
            // Disable input until the result is processed
            // update_and_validate(event, puzzle);
            return true;

        default:
            return true;
    }
}

function get_nth_move_solution(puzzle, nth_move) {
    let moves = puzzle.solution.split(" ");
    let position = 0;
    if (moves.length == 1) {
        return moves[0];
    }
    else {
        if (puzzle.orientation == "white") {
            // 1, 4, 7, 10, 13, 16, 19, 22, 25, 28
            position = (nth_move-1) * 3 + 1;
        }
        else {
            // 0, 3, 6, 9, 12, 15, 18, 21, 24, 27
            position = (nth_move-1) * 3;
        }
        return moves[position];
    }
}

function get_nth_premove(puzzle, nth_move) {
    let moves = puzzle.solution.split(" ");
    let position = 0;
    if (moves.length == 1) {
        return null;
    }
    else {
        if (puzzle.orientation == "white") {
            if (nth_move == 1) {
                return null;
            }
            // solution: "1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6 4. Ng5 Nxe4 5. Nxe4 d5"
            // 2, 5, 8, 11, 14, 17, 20, 23, 26, 29
            position = ((nth_move-1) * 3) - 1;
        }
        else {
            // solution: "e5 2. Nf3 Nc6 3. Bc4 Nf6 4. Ng5 Nxe4 5. Nxe4 d5"
            // 2, 5, 8, 11, 14, 17, 20, 23, 26, 29
            position = (nth_move-1) * 3 - 1;
        }
        return moves[position];
    }
}


function update_result(puzzle, result) {
    let time_taken = Date.now() - puzzle_start_time;
    time_taken = time_taken / 1000; // Convert to seconds
    let data = {
        "id": puzzle.id,
        "result": result,
        "time_taken": time_taken,
    };
    fetch('/update_result', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
}


// TODO: Animate the move and show result. Then get next puzzle upon user input.
function update_and_validate(event, puzzle) {
    let moves = chess.pgn().split(" ");
    let last_move = moves[moves.length - 1];
    
    let solution = get_nth_move_solution(puzzle, nth_move);

    if (last_move == solution) {
        nth_move++;
        let next_move = get_nth_premove(puzzle, nth_move);
        if (next_move == null) {
            update_result(puzzle, true);
            show_alert("Correct!", "success");
        }
        else {
            chess.move(next_move);
            board.setPosition(chess.fen(), true);
        }
    }
    else {
        update_result(puzzle, false);
        show_alert("Incorrect!", "danger");
    }

    event.chessboard.enableMoveInput(input_handler);
    return 0;
}

board.enableMoveInput(input_handler);