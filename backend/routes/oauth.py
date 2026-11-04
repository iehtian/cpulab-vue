"""OAuth 2.0 授权服务器端点"""

import json
import secrets
import time
from urllib.parse import urlencode

import jwt as pyjwt  # PyJWT 是 flask-jwt-extended 的依赖，已装好
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

import database as db_api
from config import Config
from database.redis_client import r  # 复用现有的 redis 客户端
from log_config import logger
from utils.helpers import fail, verify_password

bp = Blueprint("oauth", __name__)


@bp.route("/oauth/authorize", methods=["GET"])
@jwt_required()  # 复用现有 JWT，用户必须已登录
def authorize():
    client_id = request.args.get("client_id")
    redirect_uri = request.args.get("redirect_uri")
    state = request.args.get("state", "")

    client = db_api.get_client(client_id)
    if not client:
        return fail("未知的应用", 400)
    if not redirect_uri or redirect_uri not in client["redirect_uris"]:
        return fail("回调地址不在白名单中", 400)  # 精确匹配，防开放重定向

    code = secrets.token_urlsafe(32)
    # 授权码存 Redis：10 分钟有效，绑定用户和应用
    r.setex(
        f"oauth_code:{code}",
        600,
        json.dumps(
            {
                "user_name": get_jwt_identity(),
                "client_id": client_id,
                "redirect_uri": redirect_uri,
            }
        ),
    )

    sep = "&" if "?" in redirect_uri else "?"
    query = urlencode({"code": code, "state": state})
    return jsonify({"redirect": f"{redirect_uri}{sep}{query}"})


@bp.route("/oauth/client-info", methods=["GET"])
def client_info():
    """公开端点：授权确认页需要显示应用名称（不泄露 secret）"""
    client = db_api.get_client(request.args.get("client_id"))
    if not client:
        return fail("未知的应用", 404)
    return jsonify({"client_name": client["client_name"]})


@bp.route("/oauth/token", methods=["POST"])
def token():
    grant_type = request.form.get("grant_type")
    code = request.form.get("code")
    client_id = request.form.get("client_id")
    client_secret = request.form.get("client_secret")
    redirect_uri = request.form.get("redirect_uri")

    # 兼容 HTTP Basic 客户端认证（Fider 等 Go x/oauth2 客户端默认用 Basic 头）
    auth = request.authorization
    if not client_id and auth:
        client_id, client_secret = auth.username, auth.password

    if grant_type != "authorization_code":
        return fail("不支持的 grant_type", 400)

    # 1. 校验应用身份
    client = db_api.get_client(client_id)
    if (
        not client
        or not client_secret
        or not verify_password(client_secret, client["client_secret_hash"])
    ):
        logger.warning("token 换取失败 - 客户端认证失败: client_id={}", client_id)
        return fail("客户端认证失败", 401)

    # 2. 原子地取出并消费授权码（Redis >= 6.2 支持 GETDEL）
    raw = r.getdel(f"oauth_code:{code}")
    if not raw:
        return fail("授权码无效或已过期", 400)
    auth_code = json.loads(raw)

    # 3. 授权码必须和本次的 client、redirect_uri 对得上
    if auth_code["client_id"] != client_id or auth_code["redirect_uri"] != redirect_uri:
        logger.warning("token 换取失败 - code 与客户端不匹配: client_id={}", client_id)
        return fail("授权码与客户端信息不匹配", 400)

    # 4. 签发第三方专用 token（独立密钥 + aud 声明，与内部 JWT 隔离）
    now = int(time.time())
    access_token = pyjwt.encode(
        {
            "sub": auth_code["user_name"],
            "aud": client_id,  # 这个 token 只代表"该应用获得的授权"
            "iat": now,
            "exp": now + 7200,  # 2 小时
        },
        Config.OAUTH_JWT_SECRET,
        algorithm="HS256",
    )

    logger.info(
        "OAuth token 签发成功 | 用户: [{}] 应用: [{}]",
        auth_code["user_name"],
        client_id,
    )
    return jsonify(
        {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 7200,
        }
    )


@bp.route("/oauth/userinfo", methods=["GET"])
def userinfo():
    """第三方网站用 access_token 换取用户信息"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return fail("缺少访问令牌", 401)

    try:
        # 密钥隔离即信任边界；aud 仅作标记，关闭 PyJWT 的 audience 强制校验
        payload = pyjwt.decode(
            auth_header[7:],
            Config.OAUTH_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except pyjwt.PyJWTError as e:
        logger.warning("userinfo 查询失败 - token 校验失败: {}", e)
        return fail("访问令牌无效或已过期", 401)

    user = db_api.search_user_by_name(payload.get("sub", ""))
    if not user:
        return fail("用户不存在", 404)

    return jsonify(
        {
            "user_id": user["id"],
            "user_name": user["user_name"],
            "email": user["email"],
            "phone": user["phone"],
        }
    )
