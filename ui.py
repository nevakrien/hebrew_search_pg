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
        return sources.get(message_id, "No source available")

    def run_flask_app():
        app.run(port=5000)

    # Tkinter GUI for chatbot
    def send_message():
        user_input = user_input_box.get()
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
        user_input_box.delete(0, tk.END)

    def open_link(message_id):
        webbrowser.open(f"http://localhost:5000/source/{message_id}")

    # ... [Styling and Tkinter GUI setup remains the same]

    # Styling
    FONT =("Arial", 12)
    PRIMARY_COLOR = "#4a7a8c"##00008B  # Adjust the color as desired
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

    user_input_box = tk.Entry(input_frame, font=FONT, bg=SECONDARY_COLOR, fg=TERTIARY_COLOR)
    user_input_box.pack(side=tk.LEFT, fill=tk.X, expand=True)
    user_input_box.bind("<Return>", lambda event: send_message())

    # Send button
    send_button = tk.Button(input_frame, text="Send", command=send_message, font=FONT, bg=TERTIARY_COLOR, fg=PRIMARY_COLOR)
    send_button.pack(side=tk.RIGHT, padx=10)

    # # Source links
    # link_button = tk.Button(root, text="Open Source", command=open_link, font=FONT, bg=TERTIARY_COLOR, fg=PRIMARY_COLOR)
    # link_button.pack(padx=10, pady=10)

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



