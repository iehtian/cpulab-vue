"""每日计划相关路由：更新字段、查询某日全部计划。"""

from flask import Blueprint, jsonify, request

import database as db_api
from config import SKIP_NAMES
from log_config import logger
from utils.helpers import fail

bp = Blueprint("daily_plan", __name__)


@bp.route("/daily_plan/update", methods=["POST"])
def update_daily_plan():
    """更新每日计划字段"""
    try:
        data = request.get_json() or {}
        user_name = data.get("user_name")
        date = data.get("date")

        if not user_name or not date:
            logger.warning(
                "更新每日计划失败 - 缺少字段: user_name=%s, date=%s", user_name, date
            )
            return fail("Missing required fields: user_name, date")

        field_key_map = {"plan": "plan", "status": "status", "remark": "remark"}

        updated = []
        for payload_key, db_field in field_key_map.items():
            value = data.get(payload_key)
            if value is not None and value != "":
                db_api.upsert_plan_field(user_name, date, db_field, value)
                updated.append(db_field)

        if not updated:
            logger.warning("用户 [{}] 更新每日计划失败 - 无有效字段", user_name)
            return fail("No updatable fields provided")

        logger.info(
            "用户 [%s] 更新每日计划 | 日期: %s | 更新字段: %s",
            user_name,
            date,
            updated,
        )
        return jsonify({"updated": updated})

    except Exception as e:  # noqa: BLE001
        logger.exception("更新每日计划时发生异常: {}", e)
        return fail("Internal server error", 500)


@bp.route("/daily_plan/all", methods=["GET"])
def get_all_daily_plans():
    """获取所有用户某日的每日计划"""
    try:
        date = request.args.get("date")
        if not date:
            return fail("Date parameter is required")

        res = db_api.get_all_dateinfo_by_date(date, SKIP_NAMES)

        logger.debug("查询所有用户每日计划 | 日期: {} | 共 {} 条", date, len(res))
        return jsonify({"data": res})

    except Exception as e:  # noqa: BLE001
        logger.exception("获取所有用户每日计划时发生异常: {}", e)
        return fail("Internal server error", 500)
