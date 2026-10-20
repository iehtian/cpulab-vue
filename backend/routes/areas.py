from flask import Blueprint, jsonify, request

import database as db_api
from log_config import logger

bp = Blueprint("areas", __name__)


@bp.route("/area/add", methods=["POST"])
def add_area_api():
    """添加或更新区域信息"""
    try:
        data = request.get_json()
        parent_id = data.get("parent_id")
        space_id = data.get("space_id")
        name = data.get("name")

        if not space_id or not name:
            return jsonify({"error": "Space ID and area name are required"}), 400

        db_api.add_area(parent_id, space_id, name)
        logger.info("区域信息已添加| 名称: {}", name)
        return jsonify(
            {"success": True, "message": "Area information added successfully"}
        ), 200

    except Exception as e:  # noqa: BLE001
        logger.exception("区域信息添加/更新时发生异常: {}", e)
        return jsonify({"error": "Internal server error"}), 500


@bp.route("/area/all/<int:space_id>", methods=["GET"])
def get_area_api(space_id):
    """获取区域信息"""
    try:
        area_info = db_api.get_areas_by_space(space_id)
        return jsonify({"success": True, "data": area_info}), 200
    except Exception as e:  # noqa: BLE001
        logger.exception("获取区域信息时发生异常: {}", e)
        return jsonify({"error": "Internal server error"}), 500
