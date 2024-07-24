from flask import Flask, render_template, jsonify

app = Flask(__name__,
            static_url_path='', 
            static_folder='web/static',
            template_folder='web/templates')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_new_puzzle')
def add_new_puzzle():
    return render_template('add_new_puzzle.html')


@app.route('/get_puzzle')
def get_puzzle():
    puzzle = {
        "category": "Italian_Game Italian_Game_Classical_Variation",
        "fen": "q3k1nr/1pp1nQpp/3p4/1P2p3/4P3/B1PP1b2/B5PP/5K2 b k - 0 17",
        "pre_move": "e8d7",
        "solution": "a2e6",
        "hint_1": "Mate in 2",
        "hint_2": "Use Bishop",
        "orientation": "white"
    }
    return jsonify(puzzle)
