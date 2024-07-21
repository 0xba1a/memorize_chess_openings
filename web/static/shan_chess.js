import {Chessboard, COLOR, INPUT_EVENT_TYPE} from './node_modules/cm-chessboard/src/Chessboard.js';
import {Markers} from './node_modules/cm-chessboard/src/extensions/markers/Markers.js';
import {PROMOTION_DIALOG_RESULT_TYPE, PromotionDialog} from "./node_modules/cm-chessboard/src/extensions/promotion-dialog/PromotionDialog.js"
import {Accessibility} from "./node_modules/cm-chessboard/src/extensions/accessibility/Accessibility.js";
import {Chess} from './chess.js';


function get_puzzle() {
    fetch('/get_puzzle')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            puzzle = data;
            setup_board(data);
        });
}

get_puzzle();
let chess = new Chess();
let puzzle = null;


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

    // Make the first move
    const square_from = puzzle.pre_move[0] + puzzle.pre_move[1];
    const square_to = puzzle.pre_move[2] + puzzle.pre_move[3];
    //TODO: Handle Promotion and special moves
    const move = {from: square_from, to: square_to};
    //chess.move(move);
    //board.setPosition(chess.fen());
    
    setTimeout(() => {
        chess.move(move);
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
                    event.chessboard.setPosition(chess.fen(), true);
                });
            }
            else {
                let possible_moves = chess.moves({square: event.squareFrom, verbose: true});
                for (const possible_move of possible_moves) {
                    if (possible_move.promotion && possible_move.to === event.squareTo) {
                        event.chessboard.showPromotionDialog(event.squareTo, puzzle.color, (result) => {
                            console.log("promotion result: ", result);
                            if (result.type === PROMOTION_DIALOG_RESULT_TYPE.pieceSelected) {
                                chess.move({from: event.squareFrom, to: event.squareTo, promotion: result.piece.charAt(1)});
                                event.chessboard.setPosition(chess.fen(), true);
                            }
                            else {
                                event.chessboard.enableMoveInput(input_handler, puzzle.color);
                                event.chessboard.setPosition(chess.fen(), true);
                            }
                        });
                        return true;
                    }
                }
            }
            return move_result;

        case INPUT_EVENT_TYPE.moveInputFinished:
            update_and_validate(event, puzzle);
            return true;

        default:
            return true;
    }
}

// TODO: Animate the move and show result. Then get next puzzle upon user input.
function update_and_validate(event, puzzle) {
    if (event.legalMove == null) {
        alert("Illegal Move!");
    }
    else {
        const move = event.squareFrom + event.squareTo;
        if (move == puzzle.solution) {
            alert("Correct!");
            get_puzzle();
        }
        else {
            alert("Incorrect!");
            get_puzzle();
        }
    }
   return 0;
}

board.enableMoveInput(input_handler);