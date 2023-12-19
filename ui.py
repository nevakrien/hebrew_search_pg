import tkinter as tk
import webbrowser
import threading
from flask import Flask, render_template

def create_response_func():
    # Placeholder function for generating responses and sources
    def response_func(user_input):
        return user_input, f"the user said it!!:\n{user_input}"
    return response_func

def run_app(response_func):
    # Flask app setup
    app = Flask(__name__)

    sources = {}

    @app.route('/source/<message_id>')
    def source(message_id):
        source_text = sources.get(message_id, "No source available")
        # Use HTML and CSS to format the source text
        return f'<div style="white-space: pre-wrap;">{source_text}</div>'

    def run_flask_app():
        app.run(port=5000)

    def open_link(message_id):
        webbrowser.open(f"http://localhost:5000/source/{message_id}")

    # Tkinter GUI for chatbot
    def send_message():
        user_input = user_input_box.get("1.0", "end-1c")  # Updated for Text widget
        response, source = response_func(user_input)
        message_id = str(hash(user_input))  # Create a unique ID for each message
        sources[message_id] = source

        chatbot_response = "Chatbot says: " + response

        chat_history.config(state=tk.NORMAL)
        chat_history.insert(tk.END, "You: " + user_input + "\n" + chatbot_response + "\n")
        
        # Create a new 'View Source' button for this message
        source_button = tk.Button(chat_history, text="View Source", command=lambda: open_link(message_id))
        chat_history.window_create(tk.END, window=source_button)
        chat_history.insert(tk.END, "\n")

        chat_history.yview(tk.END)
        chat_history.config(state=tk.DISABLED)
        user_input_box.delete("1.0", tk.END)  # Updated for Text widget

    # Styling
    FONT = ("Arial", 12)
    PRIMARY_COLOR = "#4a7a8c"  # Adjust the color as desired
    SECONDARY_COLOR = "#00008B"
    TERTIARY_COLOR = "#d0e0e3"

    # Main window
    root = tk.Tk()
    root.title("Chatbot Interface")
    root.configure(bg=PRIMARY_COLOR)

    # Chat history display frame with rounded corners
    chat_frame = tk.Canvas(root, bg=PRIMARY_COLOR, highlightthickness=0)
    chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    chat_history = tk.Text(chat_frame, state=tk.DISABLED, font=FONT, bg=SECONDARY_COLOR, fg=TERTIARY_COLOR, wrap=tk.WORD)
    chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # User input box frame
    input_frame = tk.Frame(root, bg=PRIMARY_COLOR)
    input_frame.pack(padx=10, pady=10, fill=tk.X)

    # Multi-line user input box with changed caret color
    user_input_box = tk.Text(input_frame, font=FONT, bg=SECONDARY_COLOR, fg=TERTIARY_COLOR, height=4, insertbackground=TERTIARY_COLOR)
    user_input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    # user_input_box.bind("<Return>", lambda event: send_message())  # Optional: Remove if Enter should not send

    # Send button
    send_button = tk.Button(input_frame, text="Send", command=send_message, font=FONT, bg=TERTIARY_COLOR, fg=PRIMARY_COLOR)
    send_button.pack(side=tk.RIGHT, padx=10)

    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    # Start Tkinter mainloop
    root.mainloop()


if __name__=="__main__":
    # Example usage
    response_func = create_response_func()
    run_app(response_func)



