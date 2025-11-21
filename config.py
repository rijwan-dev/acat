import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

