from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import bcrypt
import hashlib
import time

app = Flask(_name_)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable real-time updates

# Function to load dictionary from wordlist.txt
def load_dictionary():
    try:
        with open("wordlist.txt", "r") as file:
            words = [line.strip() for line in file.readlines() if line.strip()]
        if not words:
            raise ValueError("Wordlist is empty")
        return words
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading wordlist: {e}. Using default dictionary.")
        return ["password", "123456", "mypassword", "hello123", "qwerty", "letmein", "admin", "welcome", "12345678"]

DICTIONARY = load_dictionary()  # Load words on startup
history = []  # Stores (input, hash, result)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/hash', methods=['POST'])
def generate_hash():
    data = request.json
    password = data.get('password')
    algorithm = data.get('algorithm', 'bcrypt')

    if not password:
        return jsonify({"error": "No password provided"}), 400

    if algorithm == 'bcrypt':
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    elif algorithm == 'sha256':
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
    elif algorithm == 'sha1':
        hashed_password = hashlib.sha1(password.encode()).hexdigest()
    elif algorithm == 'md5':
        hashed_password = hashlib.md5(password.encode()).hexdigest()
    else:
        return jsonify({"error": "Invalid algorithm selected"}), 400

    history.append({"type": "hash", "input": password, "result": hashed_password, "algorithm": algorithm})

    return jsonify({"algorithm": algorithm, "hash": hashed_password})


@socketio.on('crack_hash')
def crack_hash(data):
    """Real-time dictionary attack using WebSockets"""
    hash_to_crack = data.get('hash')

    if not hash_to_crack:
        socketio.emit('progress', {'error': 'No hash provided'})
        return

    print(f"Cracking hash: {hash_to_crack}")  # Debugging

    start_time = time.time()
    cracked = "Not found"

    for idx, word in enumerate(DICTIONARY):
        print(f"Trying: {word}")  # Debugging

        socketio.emit('progress', {'attempt': word, 'progress': int((idx + 1) / len(DICTIONARY) * 100)})

        if hashlib.md5(word.encode()).hexdigest() == hash_to_crack:
            cracked = word
            break
        elif hashlib.sha1(word.encode()).hexdigest() == hash_to_crack:
            cracked = word
            break
        elif hashlib.sha256(word.encode()).hexdigest() == hash_to_crack:
            cracked = word
            break
        elif hash_to_crack.startswith("$2b$") or hash_to_crack.startswith("$2a$"):  # bcrypt check
            if bcrypt.checkpw(word.encode(), hash_to_crack.encode()):
                cracked = word
                break

    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    history.append({"type": "crack", "input": hash_to_crack, "result": cracked, "time_taken": f"{time_taken} sec"})

    socketio.emit('progress', {'cracked_password': cracked, 'time_taken': time_taken, 'done': True})


@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(history)


if _name_ == '_main_':
    socketio.run(app, debug=True)
