import { Chessboard, COLOR, INPUT_EVENT_TYPE } from "./node_modules/cm-chessboard/src/Chessboard.js";
import { Markers } from "./node_modules/cm-chessboard/src/extensions/markers/Markers.js";
import { PromotionDialog } from "./node_modules/cm-chessboard/src/extensions/promotion-dialog/PromotionDialog.js";
import { Accessibility } from "./node_modules/cm-chessboard/src/extensions/accessibility/Accessibility.js";
import { Chess } from "./chess.js";


let board = null;
let chess = new Chess();

function reset_board() {
    board = new Chessboard(document.getElementById('board'), {
        assetsUrl: "./node_modules/cm-chessboard/assets/",
        style: { pieces: { file: "pieces/staunty.svg" }, animationDuration: 300 },
        position: chess.fen(),
        extensions: [
            { class: Markers },
            { class: PromotionDialog },
            { class: Accessibility, props: { visuallyHidden: true } }
        ]
    });
    board.setPosition(chess.fen());
}

document.getElementById('orientation').addEventListener('change', () => {
    board.setOrientation(document.getElementById('orientation').value == 1 ? COLOR.black : COLOR.white);
});

function input_handler(event) {
    console.log(event);

    switch (event.type) {
        case INPUT_EVENT_TYPE.moveInputStarted:
            return true;

        case INPUT_EVENT_TYPE.validateMoveInput:
            /*
                move: returns null if the move is illegal.
                Otherwise it returns a move object
             */
            const move = { from: event.squareFrom, to: event.squareTo, promotion: event.promotion };
            const move_result = chess.move(move);

            if (move_result) {
                event.chessboard.state.moveInputProcess.then(() => {
                    event.chessboard.setPosition(chess.fen(), true);
                });
            }
            else {
                let possible_moves = chess.moves({ square: event.squareFrom, verbose: true });
                for (const possible_move of possible_moves) {
                    if (possible_move.promotion && possible_move.to === event.squareTo) {
                        event.chessboard.showPromotionDialog(event.squareTo, puzzle.color, (result) => {
                            console.log("promotion result: ", result);
                            if (result.type === PROMOTION_DIALOG_RESULT_TYPE.pieceSelected) {
                                chess.move({ from: event.squareFrom, to: event.squareTo, promotion: result.piece.charAt(1) });
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
            document.getElementById('moves_textarea').value = chess.pgn();
            return true;

        default:
            return true;
    }
}

reset_board();
board.enableMoveInput(input_handler);
