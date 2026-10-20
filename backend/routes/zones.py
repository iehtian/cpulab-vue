from flask import Blueprint, jsonify, request

import database as db_api
from log_config import logger
from utils.helpers import fail

bp = Blueprint("zones", __name__)


@bp.route("/zone/add", methods=["POST"])
def add_zone_api():
    """添加或更新区域信息"""
    try:
        data = request.get_json()
        parent_id = data.get("parent_id")
        space_id = data.get("space_id")
        name = data.get("name")

        if not space_id or not name:
            return fail("Space ID and zone name are required")

        db_api.add_zone(parent_id, space_id, name)
        logger.info("区域信息已添加| 名称: {}", name)
        return jsonify({"message": "Zone information added successfully"})

    except Exception as e:  # noqa: BLE001
        logger.exception("区域信息添加/更新时发生异常: {}", e)
        return fail("Internal server error", 500)


@bp.route("/zone/all/<int:space_id>", methods=["GET"])
def get_zone_api(space_id):
    """获取区域信息"""
    try:
        zone_info = db_api.get_zones_by_space(space_id)
        return jsonify({"zones": zone_info})
    except Exception as e:  # noqa: BLE001
        logger.exception("获取区域信息时发生异常: {}", e)
        return fail("Internal server error", 500)
