import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://portfolio_user:portfolio_pass@localhost:5432/portfolio_blog')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
