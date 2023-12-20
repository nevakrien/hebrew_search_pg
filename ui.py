from flask import Flask, request, render_template_string, jsonify,url_for

def create_response_func():
    # Placeholder function for generating responses and sources
    def response_func(user_input):
        # Simulate generating a response and a source
        return user_input, f"אמרת:{user_input}"
    return response_func

def run_app(response_func):
    app = Flask(__name__)

    # Store chat history and sources in a dictionary
    chat_sessions = {}

    @app.route('/')
    def home():
        # Serve the chat interface
        return render_template_string('''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Chatbot Interface</title>
                <style>
                    body { font-family: Arial, sans-serif; background-color: #4a7a8c; }
                    #chat-history, #source-text {
                        background-color: #00008B; 
                        color: #d0e0e3; 
                        padding: 10px; 
                        height: 300px; 
                        overflow-y: auto; 
                        margin-bottom: 10px;
                        white-space: pre-wrap; /* Preserves whitespace and line breaks */
                    }
                    #user-input { width: calc(100% - 22px); padding: 10px; margin-bottom: 10px; }
                    #send-btn { padding: 10px 20px; background-color: #d0e0e3; color: #00008B; }
                    .message { padding: 5px; }
                    .user { color: #008000; }
                    .chatbot { color: #FF4500; }
                </style>
            </head>
            <body>
                <div id="chat-history"></div>
                <textarea id="user-input" placeholder="Type your message here..." rows="4"></textarea>
                <button id="send-btn">Send</button>
                <script>
                    function sendMessage() {
                        var userInput = document.getElementById('user-input').value;
                        fetch('/send_message', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({message: userInput})
                        }).then(response => response.json()).then(data => {
                            var chatHistory = document.getElementById('chat-history');
                            chatHistory.innerHTML += '<div class="message user">' + data.user_message + '</div>';
                            chatHistory.innerHTML += '<div class="message chatbot">' + data.chatbot_response + '</div>';
                            chatHistory.innerHTML += '<a href="' + data.source_link + '" target="_blank">View Source</a><br>';
                            chatHistory.scrollTop = chatHistory.scrollHeight;
                            document.getElementById('user-input').value = '';
                        });
                    }
                    document.getElementById('send-btn').addEventListener('click', sendMessage);
                    document.getElementById('user-input').addEventListener('keydown', function(e) {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();  // Prevent the default action to create a new line
                            sendMessage();
                        }
                    });
                </script>
            </body>
            </html>
        ''')

    @app.route('/source/<message_id>')
    def source(message_id):
        session_data = chat_sessions.get(message_id, {})
        source_text = session_data.get('source', "No source available")
        return render_template_string('''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Source Information</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    #source-text { white-space: pre-wrap; /* Preserves whitespace and line breaks */ }
                </style>
            </head>
            <body>
                <div id="source-text">{{ source_text }}</div>
            </body>
            </html>
        ''', source_text=source_text)



    @app.route('/send_message', methods=['POST'])
    def send_message():
        data = request.json
        message = data['message']
        response, source = response_func(message)

        # Create a unique ID for the chat session and store the messages and response
        session_id = str(hash(message))
        chat_sessions[session_id] = {'user_input': message, 'response': response, 'source': source}

        # Return the user message, chatbot response, and source link
        return jsonify({
            'user_message': message,
            'chatbot_response': response,
            'source_link': url_for('source', message_id=session_id)
        })



    app.run(host='localhost', port=5000, debug=True, use_reloader=False)
    #app.run(debug=True,use_reloader=False)

if __name__ == "__main__":
    response_func = create_response_func()
    run_app(response_func)
