"""认证与用户相关路由：注册、登录、认证检查、Token 刷新、个人信息、验证码。"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

import database as db_api
import verify_code
from log_config import logger
from utils.helpers import (
    hash_password,
    random_color,
    set_cookie_with_defaults,
    verify_password,
)

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
def get_register_info():
    """用户注册"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No registration data provided"}), 400

    user_name = data.get("user_name")
    password = data.get("password")
    email = data.get("email")
    phone = data.get("phone")

    if not user_name or not password or not email:
        logger.warning(
            "注册失败 - 缺少必要字段: user_name={}, password={}, email={}",
            user_name,
            password,
            email,
        )
        return jsonify(
            {"error": "Missing required fields: user_name, password, email, phone"}
        ), 400

    if db_api.search_user_by_name(user_name):
        logger.warning("注册失败 - 用户名 [{}] 已存在", user_name)
        return jsonify({"error": "User name already exists"}), 400

    user_color = random_color()
    hashed_password = hash_password(password)
    db_api.upsert_user(user_name, hashed_password, user_color, email, phone)

    access_token = create_access_token(
        identity=user_name, additional_claims={"color": user_color}
    )
    logger.info("新用户注册成功 | 用户名: [{}]", user_name)
    return jsonify(
        {
            "success": True,
            "user": {"user_name": user_name, "color": user_color},
            "access_token": access_token,
        }
    )


@bp.route("/check-auth", methods=["GET"])
@jwt_required()
def check_auth():
    """检查登录状态"""
    try:
        current_user_name = get_jwt_identity()
        user = db_api.search_user_by_name(current_user_name)
        if not user:
            logger.warning("认证检查失败 - 用户 [{}] 不存在", current_user_name)
            return jsonify({"logged_in": False, "message": "User not found"}), 401

        logger.debug("用户 [{}] 认证检查通过", current_user_name)
        return jsonify({"logged_in": True, "user_name": user["user_name"]})

    except Exception as e:  # noqa: BLE001
        logger.exception("认证检查时发生异常: {}", e)
        return jsonify({"logged_in": False, "message": "Invalid token"}), 401


@bp.route("/login", methods=["POST"])
def login():
    """用户登录"""
    data = request.get_json()
    user_name = data.get("user_name")
    password = data.get("password")

    if not user_name or not password:
        logger.warning("登录失败 - 请求缺少用户名或密码")
        return jsonify({"success": False, "message": "姓名和密码不能为空"}), 400

    user = db_api.search_user_by_name(user_name)
    if not user:
        logger.warning("登录失败 - 用户名 [{}] 不存在", user_name)
        return jsonify({"success": False, "message": "姓名或密码错误"}), 401

    if not verify_password(password, user["password"]):
        logger.warning("登录失败 - 用户 [{}] 密码错误", user_name)
        return jsonify({"success": False, "message": "姓名或密码错误"}), 401

    access_token = create_access_token(
        identity=user_name,
        additional_claims={"color": user.get("color", "#FEE2E2")},
    )
    logger.info("用户 [{}] 登录成功", user_name)

    response = jsonify(
        {
            "success": True,
            "message": "登录成功",
            "access_token": access_token,
            "user": {
                "user_name": user["user_name"],
                "color": user.get("color", "#FEE2E2"),
            },
        }
    )
    set_cookie_with_defaults(response, "user_name", user["user_name"])
    return response


@bp.route("/refresh", methods=["POST"])
@jwt_required()
def refresh():
    """刷新 JWT Token"""
    try:
        current_user_name = get_jwt_identity()
        user = db_api.search_user_by_name(current_user_name)
        if not user:
            logger.warning("Token 刷新失败 - 用户 [{}] 不存在", current_user_name)
            return jsonify({"success": False, "message": "User not found"}), 401

        new_token = create_access_token(
            identity=current_user_name,
            additional_claims={"color": user.get("color", "#FEE2E2")},
        )
        logger.debug("用户 [{}] Token 刷新成功", current_user_name)
        return jsonify({"success": True, "access_token": new_token})

    except Exception as e:  # noqa: BLE001
        logger.exception("刷新 Token 时发生异常: {}", e)
        return jsonify({"success": False, "message": "Token refresh failed"}), 500


@bp.route("/update_profile", methods=["POST"])
@jwt_required()
def update_profile():
    """更新当前用户的个人信息"""
    try:
        current_user_name = get_jwt_identity()
        data = request.get_json()

        user = db_api.search_user_by_name(current_user_name)
        if not user:
            logger.warning("更新信息失败 - 用户 [{}] 不存在", current_user_name)
            return jsonify({"error": "User not found"}), 404

        new_password = data.get("new_password")
        new_email = data.get("new_email")
        new_phone = data.get("new_phone")
        verification_code = data.get("verify_code")

        if not verification_code:
            return jsonify({"error": "Verification code is required"}), 400
        if not verify_code.verify_reset_code(current_user_name, verification_code):
            logger.warning(
                "更新信息失败 - 用户 [%s] 提供的验证码无效或已过期",
                current_user_name,
            )
            return jsonify({"error": "Invalid or expired reset code"}), 400

        hashed_password = (
            hash_password(new_password) if new_password else user.get("password")
        )

        db_api.upsert_user(
            current_user_name,
            hashed_password,
            user.get("color", None),
            new_email if new_email else user.get("email"),
            new_phone if new_phone else user.get("phone"),
        )

        updated_fields = []
        if new_password:
            updated_fields.append("password")
        if new_email:
            updated_fields.append("email")
        if new_phone:
            updated_fields.append("phone")

        logger.info(
            "用户 [%s] 更新个人信息成功 | 修改字段: %s",
            current_user_name,
            updated_fields,
        )
        return jsonify({"success": True, "message": "Profile updated successfully"})

    except Exception as e:  # noqa: BLE001
        logger.exception("更新个人信息时发生异常: {}", e)
        return jsonify({"error": "Internal server error"}), 500


@bp.route("/send_reset_code", methods=["POST"])
def send_reset_code():
    """发送密码重置验证码"""
    try:
        data = request.get_json()
        user_name = data.get("user_name")
        method = data.get("method", "sms")

        if not user_name:
            return jsonify({"error": "User name is required"}), 400

        user = db_api.search_user_by_name(user_name)
        if not user:
            logger.warning("发送验证码失败 - 用户 [{}] 不存在", user_name)
            return jsonify({"error": "User not found"}), 404

        if method == "phone":
            phone = user.get("phone")
            if not phone:
                logger.warning("发送验证码失败 - 用户 [{}] 未绑定手机号", user_name)
                return jsonify({"error": "User has no phone number on record"}), 400
            verify_code.send_reset(user_name=user_name, phone=phone)
            logger.info("向用户 [{}] 手机发送重置验证码成功", user_name)

        elif method == "email":
            email = user.get("email")
            if not email:
                logger.warning("发送验证码失败 - 用户 [{}] 未绑定邮箱", user_name)
                return jsonify({"error": "User has no email on record"}), 400
            verify_code.send_reset(user_name=user_name, email=email)
            logger.info("向用户 [{}] 邮箱发送重置验证码成功", user_name)

        else:
            logger.warning("发送验证码失败 - 不支持的方式: {}", method)
            return jsonify({"error": "Unsupported method"}), 400

        return jsonify({"success": True, "message": "Reset code sent"})

    except Exception as e:  # noqa: BLE001
        logger.exception("发送重置验证码时发生异常: {}", e)
        return jsonify({"error": "Internal server error"}), 500
