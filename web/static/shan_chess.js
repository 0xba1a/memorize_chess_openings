import {Chessboard, COLOR, INPUT_EVENT_TYPE} from './node_modules/cm-chessboard/src/Chessboard.js';
import {Markers} from './node_modules/cm-chessboard/src/extensions/markers/Markers.js';
import {PROMOTION_DIALOG_RESULT_TYPE, PromotionDialog} from "./node_modules/cm-chessboard/src/extensions/promotion-dialog/PromotionDialog.js"
import {Accessibility} from "./node_modules/cm-chessboard/src/extensions/accessibility/Accessibility.js";
import {Chess} from './chess.js';


function get_puzzle() {
    return {
        "fen": "q3k1nr/1pp1nQpp/3p4/1P2p3/4P3/B1PP1b2/B5PP/5K2 b k - 0 17",
        "solution": "e8",
        "color": COLOR.white
    }
}

let puzzle = get_puzzle();
let chess = new Chess(
    puzzle.fen
);

const board = new Chessboard(document.getElementById('board'), {
    assetsUrl: "./node_modules/cm-chessboard/assets/",
    position: puzzle.fen,
    style: {pieces: {file: "pieces/staunty.svg"}},
    orientation: puzzle.color,
    extensions: [
        {class: Markers},
        {class: PromotionDialog},
        {class: Accessibility, props: {visuallyHidden: true}}
    ]
});

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

function update_and_validate(event, puzzle) {
    if (event.legalMove == null) {
        alert("Illegal Move!");
    }
   return 0;
}

board.enableMoveInput(input_handler);