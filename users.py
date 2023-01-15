import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import string
import uuid
from sqlalchemy import MetaData, Table, create_engine, Column, String,PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import BYTEA
import psycopg2
import bcrypt

ids=[uuid.uuid4() for i in range(5)]
names=['maryem_ayadi','michael_jordan', 'moni_edhu','ally_zakhama','charles_dubois']
emails=[ names[i]+'@'+random.choice(['gmail','hotmail', 'outlook'])+'.fr' for i in range(5)]
work=['Hôpital de la Croix-Rousse, Lyon','Centre Hospitalier Universitaire de Nice ,Nice',
           'Paule de Viguier, Toulouse','Polyclinique Oxford, Cannes', 
           'Arnaud-de-Villeneuve, Montpeullier' ]

hospitals=[random.choice(work) for i in range(5)] 
#passwords
passwords=[''.join(random.sample(string.ascii_letters+ string.digits+ string.punctuation,8)) for i in range(5)]
crypted=[]
for i in passwords:
    encoded=i.encode('utf-8')
    mysalt=bcrypt.gensalt()
    i=bcrypt.hashpw(encoded, mysalt)
    crypted.append(i)

users=[]
users= pd.DataFrame(users, columns=['user_id', 'user_name', 'user_email', 'user_password',
                                    'user_hospital','user_role'])

users['user_id']=ids
users['user_name']= names
users['user_email']=emails
users['user_password']=crypted
users['user_hospital']=hospitals

users['user_role'][0]='admin'
for ind in range(1,3):
    users['user_role'][ind]='moderator'
for ind in range(3,5):
    users['user_role'][ind]='viewer'


#connecting to postgres
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