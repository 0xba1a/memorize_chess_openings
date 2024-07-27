from flask import Flask, render_template, jsonify, request
import json
import threading
from fsrs import *
from datetime import datetime, timezone, timedelta
import chess


def get_nth_move(fen, solution, player, n):
    # PGN: 1.e4 e5 2. Nf3 Nf6 3. Nxe5 Nxe4 4. Qe2 Nf6 6. Nc6+
    # Black
    # Move: 1->1, 2->4, 3->7, 4->10, 5->13
    # PreMove: 1->0, 2->3, -> 6, 4->9, 5->12
    # After Split: ['1', 'e4 e5', 'Nf3 Nf6', 'Nxe5 Nxe4', 'Qe2 Nf6', 'Nc6+']
    board = chess.Board()
    board.set_fen(fen)
    moves = solution.split(". ")
    
    if n == 1 and player == "white":
        pre_move = ""
        move = moves[1].split(" ")[0]
        return fen, pre_move, move
        
    if player == "black":
        for i in range(1, n+1):
            board.push_san(moves[i].split(" ")[0])
            board.push_san(moves[i].split(" ")[1])
        board.push_san(moves[n+1].split(" ")[0])
        move = moves[i+1].split(" ")[1]
        pre_move = moves[i+1].split(" ")[0]
        fen = board.fen()
        return fen, pre_move, move
    else:
        for i in range(1, n):
            board.push_san(moves[i].split(" ")[0])
            board.push_san(moves[i].split(" ")[1])
        # i = n-1 [Python works like this]
        move = moves[i+1].split(" ")[0]
        pre_move = moves[i].split(" ")[1]
        fen = board.fen()
        return fen, pre_move, move        
        

def split_puzzle_into_questions(puzzle):
    category = puzzle["category"]
    fen = puzzle["fen"]
    player = "white" if puzzle["orientation"] == "white" else "black"
    solution = puzzle["solution"]
    
    questions = []
    
    number_of_moves = len(solution.split(". ")) - 1
    for n in range(1, number_of_moves):
        nth_fen, pre_move, move = get_nth_move(fen, solution, player, n)
        questions.append({
            "category": category,
            "fen": nth_fen,
            "pre_move": pre_move,
            "solution": move,
            "hint_1": "",
            "hint_2": "",
            "orientation": player
        })
        
    return questions


def get_nth_sequence(fen, solution, player, n):
    board = chess.Board()
    board.set_fen(fen)
    moves = solution.split(". ")
    
    if n == 1 and player == "white":
        pre_move = ""
        move = solution
        return fen, pre_move, move
    
    if player == "black":
        # PGN: 1.e4 e5 2. Nf3 Nf6 3. Nxe5 Nxe4 4. Qe2 Nf6 6. Nc6+
        # Black
        # Move: 1->1, 2->4, 3->7, 4->10, 5->13
        # PreMove: 1->0, 2->3, -> 6, 4->9, 5->12
        # After Split: ['1', 'e4 e5', 'Nf3 Nf6', 'Nxe5 Nxe4', 'Qe2 Nf6', 'Nc6+']
        for i in range (1, n):
            board.push_san(moves[i].split(" ")[0])
            board.push_san(moves[i].split(" ")[1])
        
        split_space = (n * 3) + 1
        move = " ".join(solution.split(" ")[split_space:])
        pre_move = solution.split(" ")[split_space-1]
        return board.fen(), pre_move, move
    else:
        # PGN: 1.e4 e5 2. Nf3 Nf6 3. Nxe5 Nxe4 4. Qe2 Nf6 6. Nc6+
        # White
        # Move: 2->3, 3->6, 4->9, 5->12
        # PreMove: 2->1, -> 4, 4->7, 5->10
        # After Split: ['1', 'e4 e5', 'Nf3 Nf6', 'Nxe5 Nxe4', 'Qe2 Nf6', 'Nc6+']
        for i in range (1, n-1):
            board.push_san(moves[i].split(" ")[0])
            board.push_san(moves[i].split(" ")[1])
        pre_move = moves[n-1].split(" ")[1]
        move = " ".join(solution.split(" ")[(n-1)*3:])
        return board.fen(), pre_move, move
        

def split_puzzle_into_question_sequences(puzzle):
    category = puzzle["category"]
    fen = puzzle["fen"]
    player = "white" if puzzle["orientation"] == "white" else "black"
    solution = puzzle["solution"]
    
    sequences = []
    number_of_moves = len(solution.split(". ")) - 1
    # All sequence should lead to final move
    # For n moves, there will be n-1 sequences
    # The last single move sequence was already captured by the questions
    for n in range(1, number_of_moves): # [1 to n-1]
        seq_fen, pre_move, moves = get_nth_sequence(fen, solution, player, n)
        sequences.append({
            "category": category,
            "fen": seq_fen,
            "pre_move": pre_move,
            "solution": moves,
            "hint_1": "",
            "hint_2": "",
            "orientation": player
        })
    
    return sequences


def is_duplicate_question(question, questions_in_db):
    for question_in_db in questions_in_db:
        if question["fen"] == question_in_db["fen"] and question["solution"] == question_in_db["solution"]:
            return True
    return False


def add_question_to_db(question):
    with open("db/questions_db.json", "r") as questions_db_file:
        questions_db = json.load(questions_db_file)
        
    key = question["category"].replace(" ", "_").title()
    
    if key in questions_db:
        if is_duplicate_question(question, questions_db[key]):
            print("Question Already Exists!: ", question)
            return
        questions_db[key].append(question)
    else:
        questions_db[key] = [question]
        
    with open("db/questions_db.json", "w") as questions_db_file:
        json.dump(questions_db, questions_db_file)
    

def add_question(puzzle):
    #do nothing now
    pass

    questions = split_puzzle_into_questions(puzzle)
    for question in questions:
        card = Card()
        question["card"] = card.to_dict()
        add_question_to_db(question)
        
    questions = split_puzzle_into_question_sequences(puzzle)
    for question in questions:
        card = Card()
        question["card"] = card.to_dict()
        add_question_to_db(question)


def get_next_puzzle(names):
    with open("db/questions_db.json") as questions_db_file:
        questions_db = json.load(questions_db_file)
        
    for name in names:
        if name in questions_db:
            for question in questions_db[name]:
                card = Card.from_dict(question["card"])
                if card.due - datetime.now(timezone.utc) < 0:
                    return question
    if names:
        return None
    
    for name in questions_db.keys():
        for question in questions_db[name]:
            card = Card.from_dict(question["card"])
            if card.due - datetime.now(timezone.utc) < timedelta(seconds=0):
                return question
    return None


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


@app.route('/add_puzzle', methods=['POST'])
def add_puzzle():
    data = request.get_json()
    print(data)
    
    puzzles_db = {}
    is_new_puzzle = True
    
    key = data["category"].replace(" ", "_").title()
    print(key)
    
    with open("db/puzzles_db.json", "r") as puzzles_db_file:
        puzzles_db = json.load(puzzles_db_file)
    
    for category in puzzles_db.keys():
        if key == category:
            solution = data["solution"]
            for puzzle in puzzles_db[key]:
                if solution == puzzle["solution"]:
                    print("Puzzle Already Exists!")
                    return "Puzzle Already Exists!"
            puzzles_db[key].append(data)
            is_new_puzzle = False
            break
    
    if is_new_puzzle:
        puzzles_db[key] = [data]
        
    with open("db/puzzles_db.json", "w") as puzzles_db_file:
        json.dump(puzzles_db, puzzles_db_file)
        
    questioning_thread = threading.Thread(target=add_question, args=(data,))
    questioning_thread.start()
        
    return "Puzzle Added Successfully!"


@app.route('/get_puzzle', methods=['POST'])
def get_puzzle():
    names = request.get_json()["names"]
    return jsonify(get_next_puzzle(names))

app.run(port=5000)
