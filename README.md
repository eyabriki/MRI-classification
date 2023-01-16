# MRI-classification
**Introduction**

This is a project that allows users to upload MRI images, classify them as healthy or containing a tumor, and save them in a dataframe. It also allows authorized users to view, alter and delete the images. The project uses a convolutional neural network (CNN) model to classify the images and Flask for the RESTful API.

**Usage**

The application runs on http://localhost:5000/. 

<ins>The following endpoints for user login is available:</ins>

POST /login: Logs in the user and returns an access token

<ins>The following endpoints for MRI dataset management are available:</ins>

POST /MRI: Uploads an MRI image and classifies it as healthy or containing a tumor (protected endpoint)

GET /MRI/<string:id>: Retrieves an MRI image by its ID

PUT /MRI/<string:id>: Updates the information of an MRI image by its ID (protected endpoint)

DELETE /MRI/<string:id>: Deletes an MRI image by its ID (protected endpoint)

<ins>The following endpoints for users dataset management are available:</ins>


POST /users: Adds a new user to the users dataframe. (protected endpoint)

GET /users: Retrieves all users in the users dataframe (protected endpoint)

GET /users/<string:email>: Retrieves the information of a specific user by their email (protected endpoint)

PUT /users/<string:email>: Updates the information of a specific user by their email (protected endpoint)

DELETE /delete/<string:email>: Deletes a specific user by their email (protected endpoint)

Note: Endpoints that are protected, requires a valid token to access.POST /users: Uploads an MRI image and classifies it as healthy or containing a tumor (protected endpoint)

**Additional information**

The application uses a PostgreSQL database to store the MRI images and user information. The database configuration can be found in the config.py file.

The application uses JSON Web Tokens (JWT) for authentication and authorization. The JWT secret key can be found in the config.py file.

The application uses the Flask-RESTful library for creating the RESTful API and Flask-JWT-Extended library for handling JWT.

**Conclusion**
This project provides a simple way to classify MRI images and manage them using a RESTful API. . The usage of the endpoints is provided in the usage section and the technical details of the project are provided in the additional information section .




