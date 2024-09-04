import tkinter as tk
import requests
import random
import sqlite3

# Initialize SQLite3 database
conn = sqlite3.connect('quiz_game.db')
cursor = conn.cursor()

# Create a table to store quiz results
cursor.execute('''
    CREATE TABLE IF NOT EXISTS quiz_results (
        id INTEGER PRIMARY KEY,
        question TEXT,
        correct_answer TEXT,
        user_answer TEXT,
        result TEXT
    )
''')
conn.commit()

# Function to  question from the API
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
    global current_question, correct_answer, answer_buttons
    question, correct_answer, answers = get_trivia_question()
    
    if question:
        current_question = question
        question_label.config(text=question)
        for i in range(4):
            answer_buttons[i].config(text=answers[i], state=tk.NORMAL)
        result_label.config(text="")
    else:
        question_label.config(text="Failed to fatch question. Please try again.")

# Function to handle answer selection
def check_answer(selected_answer):
    global current_question, correct_answer
    
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
    cursor.execute('''
        INSERT INTO quiz_results (question, correct_answer, user_answer, result) 
        VALUES (?, ?, ?, ?)
    ''', (current_question, correct_answer, selected_answer, result))
    conn.commit()

# Function to display quiz results stored in the database
def show_results():
    results_window = tk.Toplevel(root)
    results_window.title("Quiz Results")
    
    results_list = tk.Listbox(results_window, width=100, height=20)
    results_list.pack(pady=20)
    
    cursor.execute('SELECT * FROM quiz_results ORDER BY id DESC')
    results = cursor.fetchall()
    
    for result in results:
        results_list.insert(tk.END, f"Question: {result[1]} | Your Answer: {result[3]} | Result: {result[4]}")

# Initialize the main window
root = tk.Tk()
root.title("Python Quiz Game")

# Create question label
question_label = tk.Label(root, text="Click 'Next Question' to start the quiz!", wraplength=400, pady=20)
question_label.pack()

# Create answer buttons
answer_buttons = []
for i in range(4):
    button = tk.Button(root, text="", width=40, pady=10, state=tk.DISABLED, command=lambda i=i: check_answer(answer_buttons[i].cget("text")))
    button.pack(pady=5)
    answer_buttons.append(button)

# Create result label
result_label = tk.Label(root, text="", pady=20)
result_label.pack()

# Create next question button
next_button = tk.Button(root, text="Next Question", command=update_question)
next_button.pack(pady=20)

# Create show results button
show_results_button = tk.Button(root, text="Show Results", command=show_results)
show_results_button.pack(pady=20)
root.mainloop()
conn.close()