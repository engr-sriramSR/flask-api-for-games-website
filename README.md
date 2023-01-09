# API for my Games Hosting Website

1.This API is built using the python flask. It has several CRUD operations to handle clients request and respond to them accordingly.
2.This API uses both SQL and NoSQL databases to store ans retrieve data.

# User data

1.Used SQL database to store all the users information. 
2.Register end point handles the new user data and stores them accordingly to the SQL database. 3.It includes the login and logout user endpoints, here JWT access token is generated and verified for the access to other endpoints.

# Games Data

1.All the games details is stored in MONGO DB database, while is a NoSQL database. 
2.The games upload and the get games information endpoints are there to store and retrieve the data from MONGO DB.

# Actions on the data

1.User information like password, email, name can be edited by the respective user.
2.Likes, comments can be given to each games available in the site.