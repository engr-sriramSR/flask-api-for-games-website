from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
import gridfs
from pymongo import MongoClient
from dotenv import load_dotenv
import os

db = SQLAlchemy()
mongodb = PyMongo()
MONGO_URL = os.getenv("MONGO_DB_URL")
MONGO_DATABASE = os.getenv("MONGO_DB_DATABASE")
client = MongoClient(MONGO_URL)
newdb = client[MONGO_DATABASE]
grid_fs = gridfs.GridFS(newdb)