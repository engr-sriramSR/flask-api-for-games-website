# API for my Games Hosting Website

<li>This API is built using the python flask. It has several CRUD operations to handle clients request and respond to them accordingly.</li>
<li>This API uses both SQL and NoSQL databases to store ans retrieve data.</li>

# User data

<li>Used SQL database to store all the users information.</li> 
<li>Register end point handles the new user data and stores them accordingly to the SQL database.</li> 
<li>It includes the login and logout user endpoints, here JWT access token is generated and verified for the access to other endpoints.</li>

# Games Data

<li>All the games details is stored in MONGO DB database, while is a NoSQL database</li> 
<li>The games upload and the get games information endpoints are there to store and retrieve the data from MONGO DB</li>

# Actions on the data

<li>User information like password, email, name can be edited by the respective user.</li>
<li>Likes, comments can be given to each games available in the site.</li>
