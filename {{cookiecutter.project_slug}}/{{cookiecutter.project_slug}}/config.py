from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
MONGODB_DB = os.getenv("MONGODB_DB")
APP_TITLE = os.getenv("APP_TITLE")
PORT = os.getenv("PORT")
