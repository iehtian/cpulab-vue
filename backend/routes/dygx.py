"""DYGX LIMS 对接路由：抓取、预约、修改、删除、CAS 登录。"""

from flask import Blueprint, jsonify, request

from dygx import (
    dygx_book,
    dygx_delete,
    dygx_fetch_with_state,
    dygx_modify,
    dygx_run_with_login,
)
from log_config import logger

bp = Blueprint("dygx", __name__)


@bp.route("/dygx_fetch", methods=["POST"])
def dygx_fetch_api():
    """使用已有 storage_state 一次性刷新登录态并抓取 LIMS 预约情况（date 可选）。"""
    try:
        data = request.get_json()
        storage_state = data.get("storage_state")
        if not storage_state:
            return jsonify({"error": "storage_state is required"}), 400

        date = data.get("date")
        result, error = dygx_fetch_with_state(storage_state, date)
        if error == "expired":
            return jsonify({"error": "expired"}), 401
        if error:
            return jsonify({"error": error}), 400
        return jsonify(result), 200
    except Exception as e:  # noqa: BLE001
        logger.exception("DYGX fetch 时发生异常: {}", e)
        return jsonify({"error": "Internal server error"}), 500


@bp.route("/dygx_book", methods=["POST"])
def dygx_book_api():
    """向 LIMS 提交一条预约"""
    try:
        data = request.get_json()
        storage_state = data.get("storage_state")
        if not storage_state:
            return jsonify({"error": "storage_state is required"}), 400

        date = data.get("date")
        start_row = data.get("start_row")
        half_hours = data.get("half_hours")
        if date is None or start_row is None or half_hours is None:
            return jsonify({"error": "date, start_row, half_hours are required"}), 400

        result, error = dygx_book(
            storage_state,
            date,
            int(start_row),
            int(half_hours),
            name=data.get("name") or "仪器使用预约",
            description=data.get("description") or "",
            count=str(data.get("count") or "1"),
        )
        if error:
            return jsonify({"error": error}), 400
        return jsonify(result), 200
    except Exception as e:  # noqa: BLE001
        logger.exception("DYGX book 时发生异常: {}", e)
        return jsonify({"error": "Internal server error"}), 500


@bp.route("/dygx_modify", methods=["POST"])
def dygx_modify_api():
    """修改一条 LIMS 预约的起止时间。"""
    try:
        data = request.get_json()
        storage_state = data.get("storage_state")
        if not storage_state:
            return jsonify({"error": "storage_state is required"}), 400

        date = data.get("date")
        start_row = data.get("start_row")
        half_hours = data.get("half_hours")
        new_start_row = data.get("new_start_row")
        new_half_hours = data.get("new_half_hours")
        if None in (date, start_row, half_hours, new_start_row, new_half_hours):
            return (
                jsonify(
                    {
                        "error": "date, start_row, half_hours, "
                        "new_start_row, new_half_hours are required"
                    }
                ),
                400,
            )

        result, error = dygx_modify(
            storage_state,
            date,
            int(start_row),
            int(half_hours),
            int(new_start_row),
            int(new_half_hours),
        )
        if error == "expired":
            return jsonify({"error": "expired"}), 401
        if error:
            return jsonify({"error": error}), 400
        return jsonify(result), 200
    except Exception as e:  # noqa: BLE001
        logger.exception("DYGX modify 时发生异常: {}", e)
        return jsonify({"error": "Internal server error"}), 500


@bp.route("/dygx_delete", methods=["POST"])
def dygx_delete_api():
    """删除一条 LIMS 预约。"""
    try:
        data = request.get_json()
        storage_state = data.get("storage_state")
        if not storage_state:
            return jsonify({"error": "storage_state is required"}), 400

        date = data.get("date")
        start_row = data.get("start_row")
        half_hours = data.get("half_hours")
        if date is None or start_row is None or half_hours is None:
            return jsonify({"error": "date, start_row, half_hours are required"}), 400

        result, error = dygx_delete(
            storage_state, date, int(start_row), int(half_hours)
        )
        if error == "expired":
            return jsonify({"error": "expired"}), 401
        if error:
            return jsonify({"error": error}), 400
        return jsonify(result), 200
    except Exception as e:  # noqa: BLE001
        logger.exception("DYGX delete 时发生异常: {}", e)
        return jsonify({"error": "Internal server error"}), 500


@bp.route("/dygx_run/login", methods=["POST"])
def dygx_run_login_api():
    """CAS SSO 登录后执行预约（需要用户名密码）"""
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        response = dygx_run_with_login(username, password)
        if not response.ok:
            return jsonify({"error": response.error}), 400
        return jsonify(response.storage_state), 200
    except Exception as e:  # noqa: BLE001
        logger.exception("DYGX run (login) 时发生异常: {}", e)
        return jsonify({"error": "Internal server error"}), 500
