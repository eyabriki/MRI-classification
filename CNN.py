import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import tensorflow as tf
import imutils
import dataset
import crop_image


X=dataset.data['MRI']
Y=dataset.data['class']





x=[]
for img in X:
    new_img=crop_image.crop_image(img)
    x.append(new_img)
    
resized_imgs = [cv2.resize(img, dsize=(32, 32)) for img in x]
x=np.squeeze(resized_imgs)
X = x.astype('float32')
X /= 255


y=Y.replace('tumor',1)
y=y.replace('healthy',0)
y=np.array(y)


#CNN model
model = tf.keras.Sequential()

model.add(tf.keras.layers.Conv2D(filters=16, kernel_size=9,
          padding='same', activation='relu', input_shape=(32, 32, 3)))
model.add(tf.keras.layers.MaxPooling2D(pool_size=2))
model.add(tf.keras.layers.Dropout(0.45))

model.add(tf.keras.layers.Conv2D(
    filters=16, kernel_size=9, padding='same', activation='relu'))
model.add(tf.keras.layers.MaxPooling2D(pool_size=2))
model.add(tf.keras.layers.Dropout(0.25))

model.add(tf.keras.layers.Conv2D(
    filters=36, kernel_size=9, padding='same', activation='relu'))
model.add(tf.keras.layers.MaxPooling2D(pool_size=2))
model.add(tf.keras.layers.Dropout(0.25))

model.add(tf.keras.layers.Flatten())

model.add(tf.keras.layers.Dense(512, activation='relu'))
model.add(tf.keras.layers.Dropout(0.15))


model.add(tf.keras.layers.Dense(1, activation='sigmoid'))


model.compile(loss='binary_crossentropy',
              optimizer=tf.keras.optimizers.Adam(),
              metrics=['acc'])


#model training and fitting
x_train, x_test,y_train , y_test=train_test_split(X,y, test_size=0.2, random_state=4)

model.fit(x_train,
          y_train,
          batch_size=128,
          epochs=200,
          validation_data=(x_test, y_test),)



#model prediction
y_hat=model.predict(x_test)

model.save(r'C:\Users\dell\Documents\projet_ws\model.h5')