import random
from flask import Flask, render_template, jsonify, request
import json
import threading
from fsrs import *
from datetime import datetime, timezone, timedelta
import chess
import db_util


def get_nth_move(fen, solution, player, n):
    # PGN: 1. e4 e5 2. Nf3 Nf6 3. Nxe5 Nxe4 4. Qe2 Nf6 5. Nc6+
    # moves = ['1', 'e4 e5 2', 'Nf3 Nf6 3', 'Nxe5 Nxe4 4', 'Qe2 Nf6 5', 'Nc6+']
    board = chess.Board()
    board.set_fen(fen)
    moves = solution.split(". ")
    
    if n == 1 and player == "white":
        pre_move = ""
        move = moves[1].split(" ")[0]
        return fen, pre_move, move
        
    if player == "black":
        for i in range(1, n):
            board.push_san(moves[i].split(" ")[0])
            board.push_san(moves[i].split(" ")[1])
        pre_move = moves[n].split(" ")[0]
        move = moves[n].split(" ")[1]
        fen = board.fen()
        return fen, pre_move, move
    else:
        for i in range(1, n-1):
            board.push_san(moves[i].split(" ")[0])
            board.push_san(moves[i].split(" ")[1])
        board.push_san(moves[n-1].split(" ")[0])
        pre_move = moves[n-1].split(" ")[1]
        move = moves[n].split(" ")[0]
        
        fen = board.fen()
        return fen, pre_move, move        
        

def split_puzzle_into_questions(puzzle):
    print(puzzle)
    puzzle_json = json.loads(puzzle["puzzle_json"])
    fen = puzzle_json["fen"]
    player = puzzle_json["orientation"]
    solution = puzzle_json["solution"]
    
    questions = []
    
    number_of_moves = len(solution.split(". ")) - 1
    for n in range(1, number_of_moves):
        nth_fen, pre_move, move = get_nth_move(fen, solution, player, n)
        questions.append({
            "puzzle_id": puzzle["id"],
            "question_json": {
                "fen": nth_fen,
                "pre_move": pre_move,
                "solution": move,
                "hint_1": "",
                "hint_2": "",
                "orientation": player
            }
        })
        
    if player == "white":
        nth_fen, pre_move, move = get_nth_move(fen, solution, player, number_of_moves)
        questions.append({
            "puzzle_id": puzzle["id"],
            "question_json": {
                "fen": nth_fen,
                "pre_move": pre_move,
                "solution": move,
                "hint_1": "",
                "hint_2": "",
                "orientation": player
            }
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
        # PGN: 1. e4 e5 2. Nf3 Nf6 3. Nxe5 Nxe4 4. Qe2 Nf6 5. Nc6+
        # moves = ['1', 'e4 e5 2', 'Nf3 Nf6 3', 'Nxe5 Nxe4 4', 'Qe2 Nf6 5', 'Nc6+']
        # 3rd Pre Move: Nxe5, 3rd Move: Nxe4 4. Qe2 Nf6 5. Nc6+
        for i in range (1, n):
            board.push_san(moves[i].split(" ")[0])
            board.push_san(moves[i].split(" ")[1])
        
        pre_move = moves[n].split(" ")[0]
        # solution.split(" ") --> ['1.', 'e4', 'e5', '2.', 'Nf3', 'Nf6', '3.', 'Nxe5', 'Nxe4', '4.', 'Qe2', 'Nf6', '5.', 'Nc6+']
        # 1->2, 2->5, 3->8, 4->11, 5->14
        split_space = (n * 3) - 1
        move = " ".join(solution.split(" ")[split_space:])
        return board.fen(), pre_move, move
    else:
        # PGN: 1. e4 e5 2. Nf3 Nf6 3. Nxe5 Nxe4 4. Qe2 Nf6 5. Nc6+
        # moves = ['1', 'e4 e5 2', 'Nf3 Nf6 3', 'Nxe5 Nxe4 4', 'Qe2 Nf6 5', 'Nc6+']
        # 3rd Pre Move: Nf6, 3rd Move: 3. Nxe5 Nxe4 4. Qe2 Nf6 5. Nc6+
        for i in range (1, n-1):
            board.push_san(moves[i].split(" ")[0])
            board.push_san(moves[i].split(" ")[1])
        board.push_san(moves[n-1].split(" ")[0])
        pre_move = moves[n-1].split(" ")[1]
        # solution.split(" ") --> ['1.', 'e4', 'e5', '2.', 'Nf3', 'Nf6', '3.', 'Nxe5', 'Nxe4', '4.', 'Qe2', 'Nf6', '5.', 'Nc6+']
        # 1->0, 2->3, 3->6, 4->9, 5->12
        split_space = (n * 3) - 3
        move = " ".join(solution.split(" ")[split_space:])
        return board.fen(), pre_move, move
        

def split_puzzle_into_question_sequences(puzzle):
    print(puzzle)
    puzzle_json = json.loads(puzzle["puzzle_json"])
    fen = puzzle_json["fen"]
    player = puzzle["orientation"]
    solution = puzzle_json["solution"]
    
    sequences = []
    number_of_moves = len(solution.split(". ")) - 1
    # All sequence should lead to final move
    # For n moves, there will be n-1 sequences
    # The last single move sequence was already captured by the questions
    for n in range(1, number_of_moves): # [1 to n-1]
        seq_fen, pre_move, moves = get_nth_sequence(fen, solution, player, n)
        sequences.append({
            "puzzle_id": puzzle["id"],
            "question_json": {
                "fen": seq_fen,
                "pre_move": pre_move,
                "solution": moves,
                "hint_1": "",
                "hint_2": "",
                "orientation": player
            }
        })
    
    return sequences


def is_duplicate_question(question, questions_in_db):
    for question_in_db in questions_in_db:
        if question["fen"] == question_in_db["fen"] and question["solution"] == question_in_db["solution"]:
            return True
    return False


def add_question_to_db(question):
    card = Card()
    question["due"] = card.due
    question["difficulty"] = card.difficulty
    question["last_review"] = None
    question["question_json"]["card"] = card.to_dict()
    
    question["id"] = db_util.get_new_question_id()
     
    cursor = db_util.get_cursor()   
    query = "INSERT INTO questions (id, puzzle_id, due, difficulty, last_review, question_json) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (question["id"], question["puzzle_id"], question["due"], question["difficulty"], question["last_review"], json.dumps(question["question_json"])))
    
    db_util.commit_and_close(cursor)


def get_puzzle_with_id(puzzle_id):
    cursor = db_util.get_cursor()
    query = "SELECT * FROM puzzles WHERE id = %s"
    cursor.execute(query, (puzzle_id,))
    puzzle= cursor.fetchone()
    db_util.commit_and_close(cursor)
    if not puzzle:
        return None
    return {
        "id": puzzle[0],
        "family": puzzle[1],
        "variation": puzzle[2],
        "sub_variation": puzzle[3],
        "type": puzzle[4],
        "orientation": puzzle[5],
        "created_at": puzzle[6],
        "modified_at": puzzle[7],
        "puzzle_json": puzzle[8]
    }
    

def add_question(puzzle_id):
    puzzle = get_puzzle_with_id(puzzle_id)
    questions = split_puzzle_into_questions(puzzle)
    for question in questions:
        add_question_to_db(question)
        
    questions = split_puzzle_into_question_sequences(puzzle)
    for question in questions:
        add_question_to_db(question)


def get_category(puzzle_id):
    cursor = db_util.get_cursor()
    query = "SELECT family, variation, sub_variation FROM puzzles WHERE id = %s"
    cursor.execute(query, (puzzle_id,))
    result = cursor.fetchone()
    db_util.commit_and_close(cursor)
    if result:
        return result[0] + ": " + result[1] + ", " + result[2]
    return "Unknown"


def get_next_puzzle(names):
    print(names) # not using this parameter now!
    query = "SELECT * FROM questions WHERE due < %s"
    cursor = db_util.get_cursor()
    cursor.execute(query, (datetime.now(timezone.utc),))
    overdue_questions = cursor.fetchall()
    db_util.commit_and_close(cursor)
    question = overdue_questions[random.randint(0, len(overdue_questions)-1)]
    print(question)
    question_json = json.loads(question[5]) # index 5 is question_json
    question_json["id"] = question[0] # index 0 is id
    question_json["category"] = get_category(question[1]) # index 1 is puzzle_id
    return question_json


def calculate_rating(result, time_taken):
    if result:
        if time_taken < 60:
            return Rating.Easy
        elif time_taken < 120:
            return Rating.Good
        else:
            return Rating.Hard
    else:
        return Rating.Again


def calculate_time_per_move(solution, time_taken):
    moves = solution.split(". ")
    number_of_moves = len(moves)
    return time_taken / number_of_moves


def update_result_in_db(id, result, time_taken):
    query = "SELECT * FROM questions WHERE id = %s"
    cursor = db_util.get_cursor()
    cursor.execute(query, (id,))
    question_text = cursor.fetchone()
    question = json.loads(question_text[5])
    card = Card.from_dict(question["card"])
    time_taken_per_move = calculate_time_per_move(question["solution"], time_taken)
    rating = calculate_rating(result, time_taken_per_move)
    card, review_log = FSRS().review_card(card, rating)
    question["card"] = card.to_dict()
    query = "UPDATE questions SET question_json = %s WHERE id = %s"
    cursor.execute(query, (json.dumps(question), id))
    db_util.commit_and_close(cursor)
    

def parse_category(category):
    if ":" not in category:
        return category, "", ""
    family = category.split(":")[0].strip()
    
    if "," not in category:
        return family, category.split(":")[1].strip(), ""
    
    variation = category.split(":")[1].split(",")[0].strip()
    sub_variation = category.split(":")[1].split(",")[1].strip()
    return family, variation, sub_variation


def is_duplicate_puzzle(family, variation, sub_variation, data):
    cursor = db_util.get_cursor()
    orientation = data["orientation"]
    query = "SELECT * FROM puzzles WHERE family = %s AND variation = %s AND sub_variation = %s AND orientation = %s"
    cursor.execute(query, (family, variation, sub_variation, orientation))
    puzzles = cursor.fetchall()
    db_util.commit_and_close(cursor)
    
    for puzzle in puzzles:
        puzzle_json = json.loads(puzzle[8])
        if data["solution"] == puzzle_json["solution"]:
            return True
    return False


def insert_new_puzzle(family, variation, sub_variation, data):
    cursor = db_util.get_cursor()
    id = db_util.get_new_puzzle_id()
    puzzle_type = "trap"
    query = "INSERT INTO puzzles (id, family, variation, sub_variation, type, orientation, created_at, puzzle_json) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (id, family, variation, sub_variation, puzzle_type, data["orientation"], datetime.now(timezone.utc), json.dumps(data)))
    db_util.commit_and_close(cursor)
    return id


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
    
    key = data["category"].title()
    print(key)
    family, variation, sub_variation = parse_category(key)
    
    if (is_duplicate_puzzle(family, variation, sub_variation, data)):
        return "Puzzle Already Exists!"
    
    puzzle_id = insert_new_puzzle(family, variation, sub_variation, data)
    
    questioning_thread = threading.Thread(target=add_question, args=(puzzle_id,))
    questioning_thread.start()
    
    return "Puzzle Added Successfully!"


@app.route('/get_puzzle', methods=['POST'])
def get_puzzle():
    names = request.get_json()["names"]
    return jsonify(get_next_puzzle(names))


@app.route('/update_result', methods=['POST'])
def update_result():
    data = request.get_json()
    print(data)
    update_result_in_db(data["id"], data["result"], data["time_taken"])
    return "Result Updated Successfully!"

app.run(host="0.0.0.0", port=5000)
