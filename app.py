from flask import Flask,request,jsonify,redirect,url_for
import os
from langchain_community.document_loaders import PyPDFLoader,TextLoader,Docx2txtLoader
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain_google_genai import GoogleGenerativeAI
#from db2 import connection
from datetime import datetime
import re
from tempfile import NamedTemporaryFile
import bcrypt
from datetime import datetime
from db2 import insertIntoDB,selectFromDB,store_feedback
import tempfile
import json
from app2 import *
app = Flask(__name__)

#conn,cursor = connection(app)

UPLOAD_FOLDER = "Uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email_address = data.get('email_address')
    password = data.get('password')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    registered_on = datetime.now()
    created_by = first_name
    created_date = datetime.now().date()
    error = None

    if len(first_name) == 0:
        return jsonify({'error' : 'Please enter your Firstname'})
    if len(last_name) == 0:
        return jsonify({'error' : 'Please enter your Lastname'})
    if len(email_address) == 0:
        return jsonify({'error' : 'Please enter your Email'})
    if len(password) == 0:
        return jsonify({'error' : 'Please enter your Password'})
        

    if not (1 <= len(first_name) <= 20):
        error = True
        return jsonify({'error' : 'Firstname length must be between 1 and 20 characters'})
        
    if not (1 <= len(last_name) <= 20):
        error = True
        return jsonify({'error' : 'Lastname length must be between 1 and 20 characters'})
        
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$', email_address):
        error = True
        return jsonify({'error' : 'Invalid email format'})
    
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',password):
        error = True
        if len(password) < 8:
            return jsonify({"error":"Password must be at least 8 characters long."})
        if not any(char.isdigit() for char in password):
            return jsonify({"error":"Password must contain at least one digit."})
        if not any(char.islower() for char in password):
            return jsonify({"error":"Password must contain at least one lowercase letter."})
        if not any(char.isupper() for char in password):
            return jsonify({"error":"Password must contain at least one uppercase letter."})
        if not any(char in '@$!%*?&' for char in password):
            return jsonify({"error":"Password must contain at least one special character (@$!%*?&)."})
    
    user = selectFromDB(app,email_address)
    if user:
        error = True
        return jsonify({'error' : 'Sorry, email already exists!'})

    if error is None:
        values = (first_name,last_name,email_address,hashed_password,registered_on,created_by,created_date)
        insertIntoDB(app,values)
        
        return jsonify({"output": "you are successfully registered"})

    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    data = request.json
    email_address = data.get('email_address')
    password = data.get('password')
    error = None

    if len(email_address) == 0:
        return jsonify({'error' : 'Please enter your Email'})
    if len(password) == 0:
        return jsonify({'error' : 'Please enter your Password'})
    
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$', email_address):
        error = True
        return jsonify({'error' : 'Invalid email format'})
    
    user = selectFromDB(app,email_address)
    if user is None:
        error = True
        return jsonify({'error':'Incorrect Email.'})
    hashed_password = user[2]
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')) == False:
        error = True
        return jsonify({'error':'Incorrect Password.'})
    if error is None:
        return redirect(url_for('upload_file'))



@app.route("/summarization", methods=["GET", "POST"])
def summarization():
    if request.method == "POST":
        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Please upload file"})

        file_name = file.filename
        file_extension = os.path.splitext(file_name)[1].lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            file.save(temp_file.name)

            if file_extension == ".pdf":
                loader = PyPDFLoader(temp_file.name)
            elif file_extension == ".docx":
                loader = Docx2txtLoader()
            elif file_extension == ".txt":
                loader = TextLoader()
            else:
                return jsonify({"error": "Unsupported file format"})

            data = loader.load()


            template = """ You have to summarize the data I am giving to you. 
            It is a tender document. So, do not miss any important points.
            Observe the entire document carefully and summarize it.
            {data}
            """
            prompt = PromptTemplate(template=template,input_variables=[ "data"])  # Remove input=["data"] line
            final_prompt = prompt.format(data=data)
            model = ChatOpenAI()
            summary=model.invoke(final_prompt) 
            tender_summary = summary.content           
            # Process feedback and store it in the database
 
            feedback = request.form.get("feedback", "bad")  # Default to "good" if feedback is not provided
            likes = request.form.get("likes", False)  # Default to True if likes are not provided
             
           
            
            created_date = datetime.now().date()
            store_feedback(tender_summary, feedback, likes,created_date)
            return jsonify({"summary": tender_summary,"status":"Feedback stored successfully!"})
        # Delete the temporary file
        os.remove(temp_file.name)
@app.route('/chatbot', methods=['POST'])
def chatbot():
    # Get data from request
    pdf_docs = request.files.getlist('pdf_docs')
    user_question = request.form['user_question']
    
    # Process PDFs
    pdf_text = get_pdf_text(pdf_docs)
    text_chunks = get_text_chunks(pdf_text)
    get_vector_store(text_chunks)
    
    # Get user input
    response = user_input(user_question)
    
    return jsonify({"response": response})
        
    # Store the entire response as a string (fallback)

# ... rest of your code ...


              
            

        

   
    
if __name__ =="__main__":
    app.run(debug = True)