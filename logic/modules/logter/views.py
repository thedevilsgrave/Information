from flask import request, abort, current_app, make_response
from logic.tools.captcha.captcha import captcha
from . import logter_blu
from logic import redis_store
from logic import constants


@logter_blu.route("/image_code")
def get_image_code():
    """生成图片验证吗并返回"""
    # 1.取到请求发过来带的参数
    image_code_id = request.args.get("imageCodeID", None)
    # 2.判断参数是否有值
    if not image_code_id:
        return abort(403)
    # 3.生成图片验证码
    name, text, picture = captcha.generate_captcha()
    # 4.保存图片验证码和带过来的参数到redis
    try:
        redis_store.set("imageCodeID_"+image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as err:
        current_app.logger.error(err)
        abort(500)
    # 5.把图片返回，并修改返回图片类型
    response = make_response(picture)
    response.headers["Content-Type"] = "image/jpg"
    return response
