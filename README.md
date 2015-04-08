# Facebook-Common-Posts
Scrapes Facebook pages and determines common posts contained in the pages (based on text) and stores them using mongodb

Dependencies:

Python Facebook SDK : https://github.com/pythonforfacebook/facebook-sdk
PyMongo: https://api.mongodb.org/python/current/installation.html

You will also need a facebook access token to run this which can be obtained at the facebook developers website.

Usage:

Open terminal and run the following command

mongod --dbpath "path-where-you-want-to-store-data"

eg. In your project folder

mkdir data

mongod --dbpath ./data

Once mongo is running in terminal, run the script to store the common posts among facebook pages you specify.


