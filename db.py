from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
import gridfs
from pymongo import MongoClient
from dotenv import load_dotenv
import os

db = SQLAlchemy()
mongodb = PyMongo()
client = MongoClient(os.getenv("MONGO_DB_URL"))
newdb = client[os.getenv("MONGO_DB_DATABASE") or 'Games']
grid_fs = gridfs.GridFS(newdb)