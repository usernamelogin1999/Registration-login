from flask import Flask,request,jsonify,redirect,url_for
import re
import bcrypt
from database.db2 import *
import os
from langchain_community.document_loaders import PyPDFLoader,TextLoader,Docx2txtLoader
from tempfile import NamedTemporaryFile
import tempfile
global error
def register_valiadate(first_name, last_name, email_address, password,registered_on,created_by,created_date):
    if len(first_name) == 0:
        return jsonify({'error': 'Please enter your Firstname'})
    if len(last_name) == 0:
        return jsonify({'error': 'Please enter your Lastname'})
    if len(email_address) == 0:
        return jsonify({'error': 'Please enter your Email'})
    if len(password) == 0:
        return jsonify({'error': 'Please enter your Password'})

    if not (1 <= len(first_name) <= 20):
        return jsonify({'error': 'Firstname length must be between 1 and 20 characters'})

    if not (1 <= len(last_name) <= 20):
        return jsonify({'error': 'Lastname length must be between 1 and 20 characters'})

    if not re.match(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$', email_address):
        return jsonify({'error': 'Invalid email format'})

    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters long."})
        if not any(char.isdigit() for char in password):
            return jsonify({"error": "Password must contain at least one digit."})
        if not any(char.islower() for char in password):
            return jsonify({"error": "Password must contain at least one lowercase letter."})
        if not any(char.isupper() for char in password):
            return jsonify({"error": "Password must contain at least one uppercase letter."})
        if not any(char in '@$!%*?&' for char in password):
            return jsonify({"error": "Password must contain at least one special character (@$!%*?&)."})
    
    user = selectFromDB(email_address)
    if user:
        return jsonify({'error': 'Sorry, email already exists!'})
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    values = (first_name, last_name, email_address, hashed_password,registered_on,created_by,created_date)
    insertIntoDB(values)
    return jsonify({'status': 'registered successfully'})
def login_validate(email_address,password):
    if len(email_address) == 0:
        return jsonify({'error' : 'Please enter your Email'})
    if len(password) == 0:
        return jsonify({'error' : 'Please enter your Password'})
    
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$', email_address):
        error = True
        return jsonify({'error' : 'Invalid email format'})
    
    user = selectFromDB(email_address)
    if user is None:
        error = True
        return jsonify({'error':'Incorrect Email.'})
    hashed_password = user[2]
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')) == False:
        error = True
        return jsonify({'error':'Incorrect Password.'})
    return jsonify({'status': 'login successfully'})
def file_validate(file):
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
            return data
        os.remove(temp_file.name)
