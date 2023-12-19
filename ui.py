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
    # Styling
    FONT = ("Arial", 12)
    MAIN_BACKGROUND_COLOR = "#4a7a8c"  # Color for the main background of the app
    CHAT_BACKGROUND_COLOR = "#00008B"  # Background color for chat history and input box
    TEXT_AND_BUTTON_COLOR = "#d0e0e3"  # Color for text and button backgrounds
    USER_TEXT_COLOR = "#008000"  # Color for the user's messages
    CHATBOT_TEXT_COLOR = "#FF4500"  # Color for the chatbot's messages
    
    def send_message():
        user_input = user_input_box.get("1.0", "end-1c")  # Get text from Text widget
        if user_input.strip():  # Check if input is not just whitespace
            response, source = response_func(user_input)
            message_id = str(hash(user_input))
            sources[message_id] = source

            chat_history.config(state=tk.NORMAL)

            # User message
            chat_history.insert(tk.END, "You: " + user_input + "\n", "user")
            chat_history.tag_configure("user", foreground=USER_TEXT_COLOR)  # Use defined color for user's messages

            # Separator line (optional)
            chat_history.insert(tk.END, "-" * 50 + "\n", "separator")

            # Chatbot response
            chatbot_response = "Chatbot says: " + response
            chat_history.insert(tk.END, chatbot_response + "\n", "chatbot")
            chat_history.tag_configure("chatbot", foreground=CHATBOT_TEXT_COLOR)  # Use defined color for chatbot's messages

            # View Source button
            source_button = tk.Button(chat_history, text="View Source", command=lambda: open_link(message_id))
            chat_history.window_create(tk.END, window=source_button)
            chat_history.insert(tk.END, "\n")

            chat_history.yview(tk.END)
            chat_history.config(state=tk.DISABLED)
            user_input_box.delete("1.0", tk.END)

    # Main window setup
    root = tk.Tk()
    root.title("Chatbot Interface")
    root.configure(bg=MAIN_BACKGROUND_COLOR)

    # Chat history display setup
    chat_frame = tk.Canvas(root, bg=MAIN_BACKGROUND_COLOR, highlightthickness=0)
    chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    chat_history = tk.Text(chat_frame, state=tk.DISABLED, font=FONT, bg=CHAT_BACKGROUND_COLOR, fg=TEXT_AND_BUTTON_COLOR, wrap=tk.WORD)
    chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # User input box setup
    input_frame = tk.Frame(root, bg=MAIN_BACKGROUND_COLOR)
    input_frame.pack(padx=10, pady=10, fill=tk.X)

    user_input_box = tk.Text(input_frame, font=FONT, bg=CHAT_BACKGROUND_COLOR, fg=TEXT_AND_BUTTON_COLOR, height=4, insertbackground=TEXT_AND_BUTTON_COLOR)
    user_input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Send button setup
    send_button = tk.Button(input_frame, text="Send", command=send_message, font=FONT, bg=TEXT_AND_BUTTON_COLOR, fg=MAIN_BACKGROUND_COLOR)
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



