import pandas as pd
import numpy as np
import cv2
from sqlalchemy import MetaData, Table, create_engine, Column, String,PrimaryKeyConstraint
from sqlalchemy import LargeBinary
from sqlalchemy.dialects.postgresql import BYTEA
import psycopg2



def get_users_dataframe():
        engine = create_engine('postgresql://postgres:root@127.0.0.1:5432/tumor_detection')
        users=pd.read_sql_table("users",engine)
        return users
    
def get_data_dataframe():
        engine = create_engine('postgresql://postgres:root@127.0.0.1:5432/tumor_detection')
        data = pd.read_sql_table("MRI_database",engine)
    # Connect to the database
        conn = psycopg2.connect(user='postgres', password='root', host='127.0.0.1', port='5432', database='tumor_detection')
        cur = conn.cursor()

        query = 'SELECT "MRI" FROM "MRI_database"'
        cur.execute(query)
        rows = cur.fetchall()
        
        images = []
        for row in rows:
            image = row[0]
            img = np.frombuffer(image, np.uint8)
            images.append(img)
    
        images_3d = [np.reshape(image, (128, 128, 3)) for image in images]

        cur.close()
        conn.close()
        data['MRI']=images_3d 
        return data
    
def apload_users(users):
    engine = create_engine('postgresql://postgres:root@127.0.0.1:5432/tumor_detection')


    metadata = MetaData()
    MRI_database = Table('users', metadata,
    Column('user_id', String(255)),
    Column('user_name', String(255)),
    Column('user_email', String(255)),
    Column('user_password', BYTEA),
    Column( 'user_hospital', String(255)),
    Column( 'user_role', String(255)),
    PrimaryKeyConstraint('user_id'))

# Create the table in the database
    metadata.create_all(engine)
    users.to_sql('users', engine, if_exists='replace', index=False, 
           dtype={'user_id': String(255),
                  'user_name': String(255),
                  'user_email': String(255),
                  'user_password': BYTEA,
                   'user_hospital': String(255)},
           schema=None,
           index_label='user_id',
           chunksize=None,
           method=None)
    
def apload_data(data):
    engine = create_engine('postgresql://postgres:root@127.0.0.1:5432/tumor_detection')
    connection = engine.connect()
    data.to_sql('MRI_database', engine, if_exists='replace', index=False,
                              dtype={'id': String(255),
                  'MRI': LargeBinary(),
                  'gender': String(255),
                  'hospital': String(255),
                   'class': String(255)},
           schema=None,
           index_label='id',
           chunksize=None,
           method=None)
    
    # Close the connection
    connection.close()