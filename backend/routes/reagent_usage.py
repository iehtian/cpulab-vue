from flask import Blueprint, jsonify, request

import database as db_api
from database.reagent_usage import EVENT_USE
from log_config import logger
from utils.helpers import fail

bp = Blueprint("reagent_usage", __name__)


@bp.route("/reagent/usage/add", methods=["POST"])
def add_reagent_usage_api():
    """添加试剂使用记录"""
    try:
        data = request.get_json()
        reagent_id = data.get("reagent_id")
        user_id = data.get("user_id")
        amount = data.get("amount")

        if not reagent_id or not user_id:
            return fail("缺少试剂或用户信息，请刷新后重试")

        db_api.add_reagent_usage(
            reagent_id, user_id, event_type=EVENT_USE, amount=amount
        )
        logger.info(
            f"Reagent usage record added for reagent_id={reagent_id}, user_id={user_id}, amount={amount}."
        )
        return jsonify({"message": "使用记录已添加"})
    except ValueError as e:
        logger.warning(f"添加试剂使用记录失败: {e}")
        return fail(str(e), 400)
    except Exception as e:  # noqa: BLE001
        logger.exception(f"Error adding reagent usage record: {e}")
        return fail("添加使用记录失败", 500)


@bp.route("/reagent/usage/list", methods=["GET"])
def get_reagent_usage_list_api():
    """获取试剂使用记录列表"""
    try:
        reagent_id = request.args.get("reagent_id", type=int)
        page = request.args.get("page", default=1, type=int)
        page_size = request.args.get("page_size", default=20, type=int)
        if not reagent_id:
            return fail("缺少试剂信息，请刷新后重试")

        usage_list = db_api.get_reagent_usage_list(reagent_id, page, page_size)
        logger.info(f"Retrieved reagent usage list for reagent_id={reagent_id}.")
        return jsonify({"usage_list": usage_list})
    except Exception as e:  # noqa: BLE001
        logger.exception(f"Error retrieving reagent usage list: {e}")
        return fail("获取使用记录列表失败", 500)
