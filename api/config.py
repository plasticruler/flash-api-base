
from sensitive import WEBDAV_HOST, WEBDAV_PASSWORD, WEBDAV_ROOT,WEBDAV_USERNAME


class BaseConfig(object):
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'thesia-1-custardise'
    JWT_SECRET_KEY = 'thesia-jwt-brickr0d'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    WEBDAV_ROOT = WEBDAV_ROOT
    WEBDAV_HOST = WEBDAV_HOST
    WEBDAV_PASSWORD = WEBDAV_PASSWORD
    WEBDAV_USERNAME = WEBDAV_USERNAME


class DevConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    DEVELOPMENT = False
    DEBUG = False
