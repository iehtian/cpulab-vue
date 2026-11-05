from flask import Blueprint, jsonify, request

import database as db_api
from log_config import logger
from utils.helpers import fail

bp = Blueprint("reagents", __name__)


@bp.route("/reagent/upsert", methods=["POST"])
def upsert_reagent_api():
    """添加或更新试剂信息"""
    try:
        data = request.get_json()
        zone_id = data.get("zone_id")
        name = data.get("name")
        CAS_number = data.get("CAS_number")
        category = data.get("category")
        capacity = data.get("capacity")
        bottle_count = data.get("bottle_count")
        specification = data.get("specification")

        if not zone_id or not name or not category:
            return fail("请填写完整：所在区域、试剂名称、类别")

        db_api.upsert_reagent(
            zone_id,
            name=name,
            CAS_number=CAS_number,
            category=category,
            capacity=capacity,
            bottle_count=bottle_count,
            specification=specification,
        )
        logger.info(
            "试剂信息已添加/更新| 区域ID: {}, 名称: {}, 类别: {}, 容量: {}, 瓶数: {}, 规格: {}".format(
                zone_id,
                name,
                category,
                capacity,
                bottle_count,
                specification,
            )
        )
        return jsonify({"message": "试剂信息已保存"})

    except Exception as e:  # noqa: BLE001
        logger.exception("试剂信息添加/更新时发生异常: {}", e)
        return fail("保存试剂信息失败", 500)


@bp.route("/reagent/open", methods=["POST"])
def open_reagent_api():
    """开瓶贴标"""
    try:
        data = request.get_json()
        Reagent_id = data.get("id")
        open_date = data.get("open_date")
        user_id = data.get("user_id")  # 默认用户ID为1，如果未提供

        if not Reagent_id or not open_date:
            return fail("请填写开封日期")

        db_api.update_open_date(
            Reagent_id,
            open_date,
        )
        logger.info(
            "试剂信息已添加/更新| 试剂ID: {}, 开封日期: {}".format(
                Reagent_id,
                open_date,
            )
        )
        db_api.open_reagent(
            Reagent_id,
            user_id,
        )
        return jsonify({"message": "试剂信息已保存"})

    except Exception as e:  # noqa: BLE001
        logger.exception("试剂信息添加/更新时发生异常: {}", e)
        return fail("开瓶贴标失败", 500)


@bp.route("/reagent/all/<int:zone_id>", methods=["GET"])
def get_reagents_by_zone_api(zone_id):
    """根据区域 ID 获取试剂信息"""
    try:
        reagent_info = db_api.get_reagents_by_zone(zone_id)
        return jsonify({"reagents": reagent_info})
    except Exception as e:  # noqa: BLE001
        logger.exception("获取试剂信息时发生异常: {}", e)
        return fail("获取试剂信息失败", 500)


@bp.route("/reagent/delete/<int:reagent_id>", methods=["DELETE"])
def delete_reagent_by_id_api(reagent_id):
    """根据试剂 ID 删除试剂信息"""
    try:
        db_api.delete_reagent_by_id(reagent_id)
        logger.info("试剂信息已删除| 试剂ID: {}".format(reagent_id))
        return jsonify({"message": "试剂已删除"})
    except Exception as e:  # noqa: BLE001
        logger.exception("删除试剂信息时发生异常: {}", e)
        return fail("删除试剂失败", 500)


@bp.route("/reagent/mark_need2restock", methods=["POST"])
def mark_reagent_need2restock_api():
    """标记试剂需要补货"""
    try:
        data = request.get_json()
        reagent_id = data.get("id")
        need2restock = data.get("need2restock")

        if reagent_id is None or need2restock is None:
            return fail("请提供试剂ID和补货状态")

        db_api.update_need2restock(reagent_id, need2restock)
        logger.info(
            "试剂补货状态已更新| 试剂ID: {}, 需要补货: {}".format(
                reagent_id,
                need2restock,
            )
        )
        return jsonify({"message": "试剂补货状态已更新"})

    except Exception as e:  # noqa: BLE001
        logger.exception("更新试剂补货状态时发生异常: {}", e)
        return fail("更新试剂补货状态失败", 500)


@bp.route("/reagent/get_need2restock_reagents", methods=["GET"])
def get_need2restock_reagents_api():
    """获取所有需要补货的试剂"""
    try:
        reagents = db_api.get_need2restock_reagents()
        return jsonify({"reagents": reagents})
    except Exception as e:  # noqa: BLE001
        logger.exception("获取需要补货的试剂信息时发生异常: {}", e)
        return fail("获取需要补货的试剂信息失败", 500)


@bp.route("/reagent/get_common_used_reagents/<int:user_id>", methods=["GET"])
def get_used_times_by_user_id_api(user_id):
    """获取用户使用次数"""
    try:
        used_times = db_api.get_common_used_reagents_by_user_id(user_id)
        return jsonify({"reagents": used_times})
    except Exception as e:  # noqa: BLE001
        logger.exception("获取用户使用次数时发生异常: {}", e)
        return fail("获取用户使用次数失败", 500)
