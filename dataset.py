import pandas as pd
import glob
import numpy as np
import cv2
import matplotlib.pyplot as plt
import random
import uuid
from sqlalchemy import MetaData, Table, create_engine, Column, String,PrimaryKeyConstraint
from sqlalchemy import LargeBinary
import psycopg2

hospitals=['Hôpital de la Croix-Rousse, Lyon','Centre Hospitalier Universitaire de Nice ,Nice',
           'Paule de Viguier, Toulouse','Polyclinique Oxford, Cannes', 
           'Arnaud-de-Villeneuve, Montpeullier' ]
gender=['female', 'male']




tumor= []
healthy=[]

for i in glob.iglob(r'C:\Users\dell\Documents\projet_ws\MRI\yes/*.jpg'):
    id=uuid.uuid4()
    sex=random.choice(gender)
    hospital= random.choice(hospitals)
    image=cv2.imread(i)
    image=cv2.resize(image, (128,128))
    tumor.append([id,image,sex,hospital,'tumor'])
    
    
for i in glob.iglob(r'C:\Users\dell\Documents\projet_ws\MRI\no/*.jpg'):
        id=uuid.uuid4()
        sex=random.choice(gender)
        hospital= random.choice(hospitals)
        image=cv2.imread(i)
        image=cv2.resize(image, (128,128))
        healthy.append([id,image,sex,hospital,'healthy'])   
        
 




dataset=tumor+healthy
data=pd.DataFrame(dataset, columns=['id','MRI','gender', 'hospital', 'class'])
data=data.sample(frac=1,random_state=1).reset_index(drop=True)


engine = create_engine('postgresql://postgres:root@127.0.0.1:5432/tumor_detection')

# Create a new table with the same columns as the DataFrame
metadata = MetaData()
MRI_database = Table('MRI_database', metadata,
    Column('id', String(255)),
    Column('MRI', LargeBinary()),
    Column('gender',String(255)),
    Column('hospital', String(255)),
    Column( 'class', String(255)),
    PrimaryKeyConstraint('id'))

#Create the table in the database
metadata.create_all(engine)
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