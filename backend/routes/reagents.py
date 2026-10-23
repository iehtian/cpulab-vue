from flask import Blueprint, jsonify, request

import database as db_api
from log_config import logger
from utils.helpers import fail

bp = Blueprint("reagents", __name__)


@bp.route("/upsert_reagent/add", methods=["POST"])
def upsert_reagent_api():
    """添加或更新试剂信息"""
    try:
        data = request.get_json()
        zone_id = data.get("zone_id")
        name = data.get("name")
        category = data.get("category")
        capacity = data.get("capacity")
        bottle_count = data.get("bottle_count")
        specification = data.get("specification")

        if not zone_id or not name or not category:
            return fail("Zone ID, reagent name, and category are required")

        db_api.upsert_reagent(
            zone_id, name, category, capacity, bottle_count, specification
        )
        logger.info(
            "试剂信息已添加/更新| 区域ID: {}, 名称: {}, 类别: {}, 容量: {}, 瓶数: {}, 规格: {}",
            zone_id,
            name,
            category,
            capacity,
            bottle_count,
            specification,
        )
        return jsonify({"message": "Reagent information added/updated successfully"})

    except Exception as e:  # noqa: BLE001
        logger.exception("试剂信息添加/更新时发生异常: {}", e)
        return fail("Internal server error", 500)

def get_reagents_by_zone_api(zone_id):
    """根据区域 ID 获取试剂信息"""
    try:
        reagent_info = db_api.get_reagents_by_zone(zone_id)
        return jsonify({"reagents": reagent_info})
    except Exception as e:  # noqa: BLE001
        logger.exception("获取试剂信息时发生异常: {}", e)
        return fail("Internal server error", 500)
