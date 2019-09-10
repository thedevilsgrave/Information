from . import index_blu


@index_blu.route('/')
def index():
    # session["name"] = "lishu"
    # # 测试log日志
    # logging.debug('测试用的debug')
    # logging.error('测试用的error')
    # logging.warning('测试用的warning')
    return "hello11world"
