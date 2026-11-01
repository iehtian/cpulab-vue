from flask import Blueprint, jsonify, request

import database as db_api
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

        db_api.add_reagent_usage(reagent_id, user_id, event_type=1, amount=amount)
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
