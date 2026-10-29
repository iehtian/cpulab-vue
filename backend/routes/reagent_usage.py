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
            return fail("Reagent ID and User ID are required")

        db_api.add_reagent_usage(reagent_id, user_id, event_type=1, amount=amount)
        logger.info(
            f"Reagent usage record added for reagent_id={reagent_id}, user_id={user_id}, amount={amount}."
        )
        return jsonify({"message": "Reagent usage record added successfully"})

    except Exception as e:  # noqa: BLE001
        logger.exception(f"Error adding reagent usage record: {e}")
        return fail("Internal server error", 500)


@bp.route("/reagent/usage/<int:reagent_id>", methods=["GET"])
def get_reagent_usage_api(reagent_id):
    """获取指定试剂的使用记录"""
    try:
        records = db_api.get_reagent_usage(reagent_id)
        return jsonify({"usage_records": records})
    except Exception as e:  # noqa: BLE001
        logger.exception(
            f"Error retrieving reagent usage records for reagent_id={reagent_id}: {e}"
        )
        return fail("Internal server error", 500)
