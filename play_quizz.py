import tkinter as tk
import requests
import random
import sqlite3

# SQLite3 database
conn = sqlite3.connect('quiz_game.db')
cursor = conn.cursor()

#  store quiz results if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS quiz_results (
                    id INTEGER PRIMARY KEY,
                    question TEXT,
                    correct_answer TEXT,
                    user_answer TEXT,
                    result TEXT
                )''')

conn.commit()

# Function to fetch question
def get_trivia_question():
    url = "https://opentdb.com/api.php?amount=1&type=multiple"
    response = requests.get(url)
    data = response.json()
    
    if data['response_code'] == 0:
        question_data = data['results'][0]
        question = question_data['question']
        correct_answer = question_data['correct_answer']
        incorrect_answers = question_data['incorrect_answers']
        
        # Combine correct and incorrect answers, then shuffle
        all_answers = incorrect_answers + [correct_answer]
        random.shuffle(all_answers)
        
        return question, correct_answer, all_answers
    else:
        return None, None, None

# Function to update the quiz question on the UI
def update_question():
    global question_label, answer_buttons, correct_answer, current_question
    question, correct_answer, answers = get_trivia_question()
    
    if question:
        current_question = question
        question_label.config(text=question)
        for i in range(4):
            answer_buttons[i].config(text=answers[i] , state=tk.NORMAL)
        result_label.config(text="")
    else:
        question_label.config(text="Failed to retrieve question. Please try again.")

# Function to handle answer selection
def check_answer(selected_answer):
    global correct_answer, current_question
    
    if selected_answer == correct_answer:
        result = "Correct"
        result_label.config(text="Correct!", fg="green")
    else:
        result = "Incorrect"
        result_label.config(text=f"Incorrect! The correct answer was: {correct_answer}", fg="red")
    
    # Disable buttons after an answer is selected
    for button in answer_buttons:
        button.config(state=tk.DISABLED)
    
    # Store the result in the SQLite database
    cursor.execute('''INSERT INTO quiz_results (question, correct_answer, user_answer, result) 
                      VALUES (?, ?, ?, ?)''', 
                   (current_question, correct_answer, selected_answer, result))
    conn.commit()

# Initialize the main window
root = tk.Tk()
root.title("Python Quiz Game")

msg_label=tk.Label(root, text="WELCOME TO MY QUIZ_GAME", wraplength=400, pady=20,bg="pink",fg="blue")
msg_label.pack()
# Create question label
question_label = tk.Label(root, text="Click 'Next Question' to start the quiz!", wraplength=400, pady=20)
question_label.pack()

# Create answer buttons
answer_buttons = []
for i in range(4):
    button = tk.Button(root, text="", width=40, pady=10, bg="pink", fg="black", command=lambda i=i: check_answer(answer_buttons[i].cget("text")))
    button.pack(pady=5)
    answer_buttons.append(button)

# Create result label
result_label = tk.Label(root, text="", pady=20)
result_label.pack()

# Create next question button
next_button = tk.Button(root, text="Next Question", command=update_question)
next_button.pack(pady=20)

# Run the main event loop
root.mainloop()

# Close the database connection when the application is closed
conn.close()