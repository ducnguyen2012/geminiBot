from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from PMC.ChatBotGemini import ChatBot
import openai

app = Flask(__name__)
CORS(app)

# Use an absolute path or configurable environment variable
FILEPATH = './Cells and Chemistry of Life.pdf'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            user_message = request.get_json().get('message')
            if not user_message:
                return jsonify({"error": "Message is required"}), 400
            
            # Debugging: Print user message
            print(f"Received message: {user_message}")

            # Call the ChatBot function
            bot_response = ChatBot(FILEPATH, user_message)

            # Debugging: Print bot response
            print(f"Bot response: {bot_response}")

            return jsonify({"response": bot_response})
        except Exception as e:
            # Print stack trace for debugging
            import traceback
            print("An error occurred:", e)
            print(traceback.format_exc())
            return jsonify({"error": "An error occurred: " + str(e)}), 500
    else:
        return render_template('index.html')

# @app.route('/mcq', methods=['GET', 'POST'])
# def mcq():
#     if request.method == 'POST':
#         try:
#             num_questions = request.form.get('numQuestions')
#             subject = request.form.get('subject')
#             tone = request.form.get('tone')
#             api_key = request.headers.get('Authorization', '').replace('Bearer ', '')

#             if not api_key:
#                 return jsonify({"error": "API key is required"}), 400

#             # Add your MCQ generation code here
#             # questions = GenerateMCQ(num_questions, subject, tone, api_key)
#             # return jsonify(questions)

#         except Exception as e:
#             print("An error occurred:", e)
#             return jsonify({"error": "An error occurred: " + str(e)}), 500
#     else:
#         return render_template('MCQ.html')

# @app.route('/validate-api-key', methods=['POST'])
# def validate_api_key():
#     api_key = request.json.get('apiKey')
#     if not api_key:
#         return jsonify({"valid": False}), 400
    
#     openai.api_key = api_key
#     try:
#         openai.Model.list()
#         return jsonify({"valid": True})
#     except openai.error.AuthenticationError:
#         return jsonify({"valid": False, "error": "Invalid API key"}), 401
#     except Exception as e:
#         print("An error occurred:", e)
#         return jsonify({"valid": False, "error": "An error occurred: " + str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
