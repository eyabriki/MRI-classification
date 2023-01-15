# MRI-classification
**Introduction
This is a project that allows users to upload MRI images, classify them as healthy or containing a tumor, and save them in a dataframe. It also allows authorized users to view, alter and delete the images. The project uses a convolutional neural network (CNN) model to classify the images and Flask for the RESTful API.
Usage
The application runs on http://localhost:5000/. The following endpoints are available:

POST /login: Logs in the user and returns an access token
POST /MRI: Uploads an MRI image and classifies it as healthy or containing a tumor (protected endpoint)
GET /MRI/<string:id>: Retrieves an MRI image by its ID
PUT /MRI/<string:id>: Updates the information of an MRI image by its ID (protected endpoint)
DELETE /MRI/<string:id>: Deletes an MRI image by its ID (protected endpoint)
