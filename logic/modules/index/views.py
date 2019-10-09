from flask import render_template, current_app, session, request, g
from flask.json import jsonify
from logic.tools.common import user_login_data
from logic.models import User, News, Category
from . import index_blu
from logic import redis_store


@index_blu.route('/')
@user_login_data
def index():
    """显示主页面"""
    # 1. 如果用户已登录,则将数据库中数据查出替换模板
    # 1.1 取到用户id
    # user_id = session.get("user_id", None)
    # user = None
    #
    # if user_id:
    #     # 尝试查询用户模型
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as err:
    #         current_app.logger.error(err)
    user = g.user

    news_list_li = []

    try:
        news_list_li = News.query.order_by(News.clicks.desc()).limit(8)
    except Exception as err:
        current_app.logger.error(err)

    news_dict = []
    for news in news_list_li:
        news_dict.append(news.to_basic_dict())

    # 查询分类数据,通过模板渲染出来
    kinds = Category.query.all()

    kinds_list = []
    for kind in kinds:
        kinds_list.append(kind.to_dict())

    data = {
        "user": user.to_dict() if user else None,
        "news_list": news_dict,
        "news_kind": kinds_list
    }

    return render_template("news/index.html", data=data)


@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")


@index_blu.route("/news_list")
def news_list():
    """获取首页新闻数据"""
    # 1. 获取参数
    cid = request.args.get("cid", "1")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "10")

    # 2. 校验参数
    try:
        page = int(page)
        cid = int(cid)
        per_page = int(per_page)
    except Exception as er:
        current_app.logger.error(er)
        return jsonify(errno="5000", errmsg="参数错误")

    filters = [News.status == 0]
    # 查询的不是最新的数据
    if cid !=1:
        # 需要添加条件
        filters.append(News.category_id == cid)
    try:
        # 查数据
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno="5000", errmsg="查询错误")

    # 取当前页的数据
    new_list = paginate.items
    # paginate.pages取到总页数
    page_quantity = paginate.pages
    wyf_page = paginate.page

    # 将模型对象转换成字典列表
    news_dict = []
    for news in new_list:
        news_dict.append(news.to_basic_dict())

    data = {
        "totalPage": page_quantity,
        "newsList": news_dict,
        "currentPage": wyf_page
    }

    return jsonify(errno="2000", errmsg="OK", data=data)



