import {Chessboard, FEN, INPUT_EVENT_TYPE} from './node_modules/cm-chessboard/src/Chessboard.js';
import {Markers} from './node_modules/cm-chessboard/src/extensions/markers/Markers.js';
import {Chess} from './chess.js';


function get_puzzle() {
    return {
        "fen": "q3k1nr/1pp1nQpp/3p4/1P2p3/4P3/B1PP1b2/B5PP/5K2 b k - 0 17",
        "solution": "e8",
        "orientation": "white"
    }
}

let puzzle = get_puzzle();
let chess = new Chess(
    puzzle.fen
);
let piece = null
let color = null
let start_square = null
let end_square = null
let move = null;

const board = new Chessboard(document.getElementById('board'), {
    assetsUrl: "./node_modules/cm-chessboard/assets/",
    position: puzzle.fen,
    style: {pieces: {file: "pieces/staunty.svg"}},
    extensions: [{class: Markers}]
});

board.enableMoveInput((event) => {
    console.log(event);
    switch (event.type) {
        case INPUT_EVENT_TYPE.moveInputStarted:
            color = get_color(event.piece);
            piece = get_piece(event.piece);
            start_square = event.square;
            return true;

        case INPUT_EVENT_TYPE.moveInputFinished:
            if (piece == null) {
                // Cancelled Move
                return true;
            }
            if (start_square != event.squareFrom) {
                console.log("Didn't capture the starting square properly!\nSomething is wrong in the code.");
                Exception("Didn't capture the starting squre properly!\nSomething is wrong in the code.");
            }
            end_square = event.squareTo;
            move = construct_move(start_square, end_square, piece, color);
            validate(move, puzzle);
            return true;

        case INPUT_EVENT_TYPE.moveInputCanceled:
            piece = color = null;
            start_square = null;
            end_square = null;
            return true;

        default:
            return true;
    }
});

function get_color(piece) {
    return piece[0].toLowerCase();
}

function get_piece(piece) {
    piece = piece[1].toLowerCase();
    if (piece == "p") {
        return "";
    }
    return piece.toUpperCase();
}

function construct_move(start_square, end_square, piece, color) {
    // TODO: Handle Castling, En passant, Promotion
    // TODO: Handle when two pieces of same type can move to the same square
    return piece + end_square;
}

function validate(move, puzzle) {
    if (move == puzzle.solution) {
        alert("Congratulations! You solved the puzzle!");
    } else {
        alert("Oops! That's not the right move. Try again!");
    }
}