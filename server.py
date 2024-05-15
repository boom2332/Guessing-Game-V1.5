import socket
import random
import json

host = ""
port = 7777
banner = """
== Guessing Game v1.0 ==
Enter your name:"""

def generate_random_int(low, high):
    return random.randint(low, high)

def load_leaderboard(file_path="leaderboard.json"):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_leaderboard(leaderboard, file_path="leaderboard.json"):
    with open(file_path, "w") as f:
        json.dump(leaderboard, f)

def get_difficulty_range(difficulty):
    if difficulty == 'easy':
        return 1, 50
    elif difficulty == 'medium':
        return 1, 100
    elif difficulty == 'hard':
        return 1, 500
    else:
        return 1, 50  # default to easy

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(5)

print(f"server is listening on port {port}")
leaderboard = load_leaderboard()

while True:
    conn, addr = s.accept()
    print(f"new client: {addr[0]}")
    conn.sendall(banner.encode())
    
    name = conn.recv(1024).decode().strip()
    if name not in leaderboard:
        leaderboard[name] = {"score": float('inf'), "difficulty": "easy"}
    conn.sendall(f"Hello {name}! Choose difficulty: easy, medium, hard:".encode())

    difficulty = conn.recv(1024).decode().strip().lower()
    if difficulty not in ['easy', 'medium', 'hard']:
        difficulty = 'easy'
    leaderboard[name]["difficulty"] = difficulty

    low, high = get_difficulty_range(difficulty)
    guessme = generate_random_int(low, high)
    conn.sendall(f"Guess a number between {low} and {high}:".encode())
    
    attempts = 0
    while True:
        client_input = conn.recv(1024).decode().strip()
        if client_input.lower() == 'quit':
            conn.sendall(b"Goodbye!")
            conn.close()
            break
        
        try:
            guess = int(client_input)
        except ValueError:
            conn.sendall(b"Invalid input. Please enter a number: ")
            continue

        attempts += 1
        if guess == guessme:
            score = attempts
            if score < leaderboard[name]["score"]:
                leaderboard[name]["score"] = score
            conn.sendall(f"Correct Answer! Your score: {score}\nPlay again? (yes/no)".encode())
            
            replay = conn.recv(1024).decode().strip().lower()
            if replay == 'yes':
                conn.sendall(f"Choose difficulty: easy, medium, hard:".encode())
                difficulty = conn.recv(1024).decode().strip().lower()
                if difficulty not in ['easy', 'medium', 'hard']:
                    difficulty = 'easy'
                leaderboard[name]["difficulty"] = difficulty
                low, high = get_difficulty_range(difficulty)
                guessme = generate_random_int(low, high)
                attempts = 0
                conn.sendall(f"Guess a number between {low} and {high}:".encode())
            else:
                conn.sendall(b"Goodbye!")
                conn.close()
                break
        elif guess > guessme:
            conn.sendall(b"Guess Lower! Enter guess: ")
        elif guess < guessme:
            conn.sendall(b"Guess Higher! Enter guess: ")
    
    save_leaderboard(leaderboard)
    print("Current Leaderboard:")
    for player, stats in leaderboard.items():
        print(f"{player} - Score: {stats['score']} (Difficulty: {stats['difficulty']})")