from datetime import date

from flask import Blueprint, jsonify, request

import database as db_api
from log_config import logger
from utils.helpers import fail

bp = Blueprint("duty_log", __name__)


@bp.route("/duty_log/get_duty", methods=["GET"])
def get_all_duty_logs():
    try:
        week_start = request.args.get("week_start")
        if not week_start:
            return fail("请指定周开始日期")
        week_start = date.fromisoformat(week_start)
        instrument_id = request.args.get("instrument_id")
        res = db_api.get_duty_log(instrument_id, 30, week_start)
        return jsonify(res)
    except Exception as e:  # noqa: BLE001
        logger.exception("获取值班日志时发生异常: {}", e)
        return fail("获取值班日志失败", 500)


@bp.route("/duty_log/get_roster", methods=["GET"])
def get_duty_roster():
    try:
        week_start = request.args.get("week_start")
        if not week_start:
            return fail("请指定周开始日期")
        week_start = date.fromisoformat(week_start)
        instrument_id = request.args.get("instrument_id")
        res = db_api.get_duty_roster(instrument_id, 30, week_start)
        return jsonify(res)
    except Exception as e:  # noqa: BLE001
        logger.exception("获取值班日志时发生异常: {}", e)
        return fail("获取值班日志失败", 500)
