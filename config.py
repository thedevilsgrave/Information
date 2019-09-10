import logging

from redis import StrictRedis


class Config(object):
    """项目的配置"""
    SECRET_KEY = "P+gASq3hwoH+ZNXDviyzqWscSgpbfDmsgOYwmAWvCoyVRORNFgNiCJBENpWCsloP"
    # 为Mysql添加配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 为Redis设置配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # 为session配置
    SESSION_TYPE = "redis"
    # 设置session保存到redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 设置是否对session进行签名
    SESSION_USE_SIGNER = True
    # 设置session是否一直存在，设置过期时间
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 86300 * 2
    LOG_LEVEL = logging.DEBUG


class DevelopmentConfig(Config):
    DEBUG = True


class ProduceConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.WARNING


class TestingConfig(Config):
    DEBUG = True
    TESTING = True


config_dict = {
    "development": DevelopmentConfig,
    "produce": ProduceConfig,
    "testing": TestingConfig
}