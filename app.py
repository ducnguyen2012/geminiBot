
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from io import BytesIO
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores.faiss import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()
genai.configure(api_key=os.getenv('KEY'))

def get_pdf_text(pdf_docs):
    text = ''
    if pdf_docs is not None:
        if isinstance(pdf_docs, list):
            for pdf in pdf_docs:
                pdf_reader = PdfReader(BytesIO(pdf.read()))
                for page in pdf_reader.pages:
                    text += page.extract_text()
        else:  # If pdf_docs is a single file
            pdf_reader = PdfReader(BytesIO(pdf_docs.read()))
            for page in pdf_reader.pages:
                text += page.extract_text()
    return text



def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001', google_api_key=os.getenv('KEY'))
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local('faiss-index')

def get_conversational_chain():
    prompt_template = '''
    Answer the question as detailed as possible from the provided context.\
    The answer must be in 50 words and details.\ 
    If the question not related to context, just say: the question not relevant to the context!\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    '''
    model = ChatGoogleGenerativeAI(model='gemini-pro', temperature=0.1, google_api_key=os.getenv('KEY'))

    prompt = PromptTemplate(template=prompt_template, input_variables=['context', 'question'])
    chain = load_qa_chain(model, chain_type='stuff', prompt=prompt)
    return chain

def ChatBot(pdf_path: str,user_question: str):
    embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001', google_api_key=os.getenv('KEY'))

    try:
        new_db = FAISS.load_local('faiss-index', embeddings, allow_dangerous_deserialization=True)
    except ValueError as e:
        print("error!")
        return

    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()

    response = chain(
        {'input_documents': docs, 'question': user_question}
    )

    return response['output_text']

# print(ChatBot("./Cells and Chemistry of Life.pdf", "What is a cell? answer in detail!"))






from flask import Flask, jsonify, request, render_template




app = Flask(__name__)


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
    app.run(host='0.0.0.0', debug=True)
