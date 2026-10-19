"""空间管理路由：添加/更新空间、获取全部空间。"""

from flask import Blueprint, jsonify, request

import database as db_api
from log_config import logger

bp = Blueprint("spaces", __name__)


@bp.route("/space/upsert", methods=["POST"])
def upsert_space_api():
    """添加或更新空间信息"""
    try:
        data = request.get_json()
        name = data.get("name")

        if not name:
            return jsonify({"error": "Space name is required"}), 400

        db_api.upsert_space(name)
        logger.info("空间信息已添加/更新 | 名称: %s", name)
        return jsonify(
            {"success": True, "message": "Space information upserted successfully"}
        ), 200

    except Exception as e:  # noqa: BLE001
        logger.exception("空间信息添加/更新时发生异常: {}", e)
        return jsonify({"error": "Internal server error"}), 500


@bp.route("/space/all", methods=["GET"])
def get_all_spaces_api():
    """获取所有空间信息"""
    try:
        spaces = db_api.get_all_spaces()
        logger.debug("查询所有空间信息 | 共 {} 条", len(spaces))
        return jsonify({"success": True, "spaces": spaces}), 200

    except Exception as e:  # noqa: BLE001
        logger.exception("查询所有空间信息时发生异常: {}", e)
        return jsonify({"error": "Internal server error"}), 500
