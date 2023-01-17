import json
import pandas as pd
import glob
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import random
import uuid
import tensorflow as tf 
import bcrypt
import postgres_tables
import crop_image
from flask import Flask, make_response, request
from flask_restful import Api, Resource, reqparse
from flask_smorest import abort
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required, create_access_token,get_jwt
from sqlalchemy import MetaData, Table, create_engine, Column, String,PrimaryKeyConstraint, engine_from_config, update
from sqlalchemy import LargeBinary
import psycopg2

app = Flask(__name__)
api = Api(app)
app.config["DEBUG"] = True
# Set the secret key
app.config['JWT_SECRET_KEY'] = 'my_secret_key'

# Initialize Flask-JWT-Extended
jwt = JWTManager(app)
jwt.init_app(app)

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('user_email')
    password = request.json.get('user_password')
    password = password.encode('utf-8')

    
    users=postgres_tables.get_users_dataframe() 
    email_exists = users[users['user_email'] == email].empty
    if email_exists:
        return {"message": "incorrect email"}, 401
    
    hashed_password = users[users['user_email'] == email]['user_password'].tolist()[0]
    #hashed_password = bytes.fromhex(hashed_password)
    if not bcrypt.checkpw(password, hashed_password):
        return {"message": "incorrect password"}, 401
    
    row= users.index[users['user_email'] ==email].tolist()[0]
    role=users['user_role'][row]
    # Identity can be any data that is json serializable
    access_token = create_access_token(identity={"email": email, "role": role}) 
    return access_token , 200



#MRIs
@app.route('/MRI/<int:x>')
def get_id(x):
    data=postgres_tables.get_data_dataframe()
    # Get the value of the 'id' column for the specified row
    id_value = data['id'][x]
    return str(id_value)

@app.route('/MRI/<string:id>')
def get_MRI_by_id(id):
    data=postgres_tables.get_data_dataframe()
    try:
        row = data[data['id'] == id]
    except row is None:
        abort(404, message="MRI not found.")
        
    # Get the values of the other columns for the row
    gender = row['gender'].values[0]
    hospital = row['hospital'].values[0]
    mri_class = row['class'].values[0]

    # Create a result dictionary with the values of the other columns
    result = {'gender': gender, 'hospital': hospital, 'class': mri_class}
    
    # Get the MRI image from the 'MRI' column
    img = row['MRI'].values[0]
    
    # Encode the image as a JPEG
    _, img_encoded = cv2.imencode('.jpg', img)

    # Create a response object with the encoded image
    response = make_response(img_encoded.tobytes())

    # Set the 'Content-Type' header to 'image/jpeg'
    response.headers.set('Content-Type', 'image/jpeg')
    
    return (response, result)

@app.post('/MRI') 
@jwt_required()
def add_MRI () :
    claims = get_jwt_identity()
    role = claims.get('role')
    if role not in ['admin', 'moderator']:
        return {"message": "You are not authorized to perform this action."}, 403
    
    # Read the values of the other columns from the request payload
    payload = request.get_json()
    gender = payload.get('gender')
    hospital= payload.get('hospital')
    
    loaded_model = tf.keras.models.load_model(r'C:\Users\dell\Documents\projet_ws\model.h5')
    data=postgres_tables.get_data_dataframe()

    image_list = glob.glob(r'C:\Users\dell\Documents\projet_ws\new/*.jpg')

    #Sort the list based on the modification time of the files
    image_list.sort(key=lambda x: os.path.getmtime(x))

    #Get the last image in the list (the one with the latest modification time)
    last_image = image_list[-1]

# Read the image
    image = cv2.imread(last_image)

   
    # Resize the image
    image = cv2.resize(image, (128, 128))
    
    # Check if the image was read successfully
    if image is None:
        return {'message': 'MRI not found'}, 400
    x=[]

    new_img=crop_image.crop_image(image)
    x.append(new_img)
    
    resized_imgs = [cv2.resize(img, dsize=(32, 32)) for img in x]
    x=np.squeeze(resized_imgs)
    X = x.astype('float32')
    X /= 255
    X = np.expand_dims(x, axis=0)


    # Predict the class of the image
    y_hat = loaded_model.predict(X)
    if y_hat == 0:
        label = 'healthy'
    else:
        label = 'tumor'

    # Create a new row for the image in the DataFrame
    new_row = {'id': uuid.uuid4(), 'MRI': image, 'gender': gender, 'hospital':hospital, 'class': label }
    
    
    
    data = data.append(new_row, ignore_index=True).reset_index(drop=True)
    postgres_tables.apload_data(data)

    return {'message':'MRI added'}, 200


@app.route('/MRI/<string:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def alter_MRI(id):
    claims = get_jwt_identity()
    role = claims.get('role')
    if role not in ['admin', 'moderator']:
       return {"message": "You are not authorized to perform this action."}, 403
    
    payload=request.get_json()
    gender=payload.get('gender') 
    hospital=payload.get('hospital')
    label=payload.get('class')
    
    data=postgres_tables.get_data_dataframe()
    try:
        row = data.index[data['id'] == id]
    except IndexError:
        abort(404, message='ID does not exist')
    
    
    if gender is not None:
        data['gender'][row.tolist()[0]]=gender
    if hospital is not None:
        data['hospital'][row.tolist()[0]]=hospital
    if label is not None:
       data['class'][row.tolist()[0]]=label
    
    postgres_tables.apload_data(data)
    return  {'messgae':'information altered'}, 200

@app.route('/delete/<string:id>', methods=['DELETE'])
@jwt_required()
def delete_MRI(id):
    claims = get_jwt_identity()
    role = claims.get('role')
    if role not in ['admin']:
        return {"message": "You are not authorized to perform this action."}, 403
    
    data=postgres_tables.get_data_dataframe()
    try:
        row=data.index[data['id'] ==id]
    except IndexError:
        abort(404, message="user not found.")
        
    data=data.drop(row.tolist()[0]) 
       
    
    postgres_tables.apload_data(data)
    return {"message": "MRI deleted."}
    
#users    
@app.route('/users/<string:name>')
def get_doctor(name):
   users=postgres_tables.get_users_dataframe()
   try:
      row = users.index[users['user_name'] == name].tolist()[0]
   except IndexError:
      raise KeyError("there is no physician with that name!")

   info = {
    'id':users['user_id'][row],
    'name': users['user_name'][row],
    'email': users['user_email'][row],
    'hospital': users['user_hospital'][row],
    'role':users['user_role'][row]
}
   return info




@app.post('/users')
@jwt_required()
def add_doctor():
    claims = get_jwt_identity()
    role = claims.get('role')
    if role not in ['admin', 'moderator']:
       return {"message": "You are not authorized to perform this action."}, 403
    
    payload=request.get_json()
    name=payload.get('user_name')
    email=payload.get('user_email')
    password=payload.get('user_password')
    hospital=payload.get('user_hospital')
    role=payload.get('user_role')
    
    encoded=password.encode('utf-8')
    mysalt=bcrypt.gensalt()
    password=bcrypt.hashpw(encoded, mysalt)
    
    users=postgres_tables.get_users_dataframe()
    if name is None or email is None or password is None or hospital is None:
        abort(404, message="you need to apload all physician's information") 
    if  users['user_name'].isin([name]).any():
        abort(404, message="the physician already exists")
        
    new_row = {'user_id': uuid.uuid4(), 'user_name': name, 'user_email': email,'user_password':password,
                   'user_hospital':hospital, 'user_role':role} 
    users=users.append(new_row,ignore_index=True).reset_index(drop=True)  
    postgres_tables.apload_users(users)
    return {'message':'physician added'},200





@app.route('/users/<string:user_name>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_doctor(user_name):
    claims = get_jwt_identity()
    role = claims.get('role')
    if role not in ['admin', 'moderator']:
        return {"message": "You are not authorized to perform this action."}, 403
    
    payload=request.get_json()
    name=payload.get('user_name')
    email=payload.get('user_email')
    password=payload.get('user_password')
    hospital=payload.get('user_hospital')
    role=payload.get('user_role')
    
    users=postgres_tables.get_users_dataframe()
    try:
       row= users.index[users['user_name'] ==user_name].tolist()[0]
    except IndexError:
        raise KeyError("there is no physician with that name!")
    
    if name is not None:
        users['user_name'][row] = name
    if email is not None:
        users['user_email'][row] = email
    if password is not None:
        users['user_password'][row] = password
    if hospital is not None:
        users['user_hospital'][row] = hospital
    if role is not None:
        users['user_role'][row] = role
          
    postgres_tables.apload_users(users)
    return {'message':'information updated'},200


@app.delete('/users/<string:user_name>')
@jwt_required()
def delete_doctor(user_name):
    claims = get_jwt_identity()
    role = claims.get('role')
    if role not in ['admin']:
        return {"message": "You are not authorized to perform this action."}, 
    
    users=postgres_tables.get_users_dataframe()
    try:
        row=users.index[users['user_name'] ==user_name]
    except IndexError:
        abort(404, message="user not found.")
        
    users=users.drop(row.tolist()[0])    
    
    postgres_tables.apload_users(users)
    return {"message": "user deleted."}
   
if __name__=='__main__':
    app.run(debug=True)