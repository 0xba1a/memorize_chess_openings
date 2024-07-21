import {Chessboard, FEN, INPUT_EVENT_TYPE} from './node_modules/cm-chessboard/src/Chessboard.js';
import {Markers} from './node_modules/cm-chessboard/src/extensions/markers/Markers.js';

const board = new Chessboard(document.getElementById('board'), {
    assetsUrl: "./node_modules/cm-chessboard/assets/",
    position: FEN.start,
    style: {pieces: {file: "pieces/staunty.svg"}},
    extensions: [{class: Markers}]
});

board.enableMoveInput((event) => {
    console.log(event);
    if (event.type == INPUT_EVENT_TYPE.moveInputStarted ||
        event.type == INPUT_EVENT_TYPE.validateMoveInput) {
        return true;
    }
});