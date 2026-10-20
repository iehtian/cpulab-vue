"""预约相关路由：提交、取消、按日期/用户/区间查询。"""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

import database as db_api
from log_config import logger
from utils.helpers import fail

bp = Blueprint("bookings", __name__)


@bp.route("/info_save", methods=["POST"])
@jwt_required()
def save_info():
    """保存预约信息"""
    try:
        current_user_name = get_jwt_identity()
        data = request.get_json()

        instrument = data.get("instrument") or "a_instrument"
        date = data.get("date")
        slots_ids = data.get("slots")

        if not date or not slots_ids:
            logger.warning(
                "用户 [%s] 提交预约失败 - 缺少必要字段: date=%s, slots=%s",
                current_user_name,
                date,
                slots_ids,
            )
            return fail("Missing required fields: date, slots, user_name")

        if not isinstance(slots_ids, list) or len(slots_ids) == 0:
            logger.warning(
                "用户 [%s] 提交预约失败 - slots 格式错误: %s",
                current_user_name,
                slots_ids,
            )
            return fail("slots_ids must be a non-empty array")

        logger.info(
            "用户 [%s] 请求预约 | 仪器: %s | 日期: %s | 时间段: %s",
            current_user_name,
            instrument,
            date,
            slots_ids,
        )

        search_by_date_result = db_api.search_booking_by_date(instrument, date)
        if search_by_date_result:
            booked_times = [slot["time_slot_id"] for slot in search_by_date_result]
            for slot in slots_ids:
                if slot in booked_times:
                    logger.warning(
                        "用户 [%s] 预约冲突 | 仪器: %s | 日期: %s | 时间段 %s 已被占用",
                        current_user_name,
                        instrument,
                        date,
                        slot,
                    )
                    return fail(f"Time slot {slot} is already booked", 409)

        successful_slots = []
        for slot in slots_ids:
            db_api.upsert_booking(current_user_name, instrument, date, slot)
            successful_slots.append(slot)

        logger.info(
            "用户 [%s] 预约成功 | 仪器: %s | 日期: %s | 时间段: %s | 共 %d 个",
            current_user_name,
            instrument,
            date,
            successful_slots,
            len(successful_slots),
        )
        return jsonify(
            {
                "message": (
                    f"Successfully booked {len(successful_slots)} "
                    f"time slots for {current_user_name} on {date}"
                ),
                "booked_slots": successful_slots,
            }
        )

    except Exception as e:  # noqa: BLE001
        logger.exception("保存预约时发生异常: {}", e)
        return fail("Internal server error", 500)


@bp.route("/cancel_booking", methods=["POST"])
@jwt_required()
def cancel_booking():
    """取消预约"""
    try:
        current_user_name = get_jwt_identity()
        data = request.get_json()

        instrument = data.get("instrument") or "a_instrument"
        date = data.get("date")
        slots = data.get("slots")

        if not date or not slots:
            logger.warning(
                "用户 [%s] 取消预约失败 - 缺少字段: date=%s, slots=%s",
                current_user_name,
                date,
                slots,
            )
            return fail("Missing required fields: date, slots")

        if not isinstance(slots, list) or len(slots) == 0:
            logger.warning(
                "用户 [%s] 取消预约失败 - slots 格式错误: %s", current_user_name, slots
            )
            return fail("slots must be a non-empty array")

        logger.info(
            "用户 [%s] 请求取消预约 | 仪器: %s | 日期: %s | 时间段: %s",
            current_user_name,
            instrument,
            date,
            slots,
        )

        search_by_date_result = db_api.search_booking_by_date(instrument, date)
        if not search_by_date_result:
            logger.warning(
                "用户 [%s] 取消预约失败 - 指定日期 %s 无预约记录",
                current_user_name,
                date,
            )
            return fail("No bookings found for the specified date", 404)

        booked_slot_ids = [slot["time_slot_id"] for slot in search_by_date_result]
        for slot in slots:
            if slot not in booked_slot_ids:
                logger.warning(
                    "用户 [%s] 取消预约失败 - 时间段 %s 在 %s 不存在",
                    current_user_name,
                    slot,
                    date,
                )
                return fail(f"Time slot {slot} is not booked", 404)

        deleted_count = db_api.delete_bookings_by_slots(instrument, date, slots)

        logger.info(
            "用户 [%s] 取消预约成功 | 仪器: %s | 日期: %s | 时间段: %s | 共取消 %d 个",
            current_user_name,
            instrument,
            date,
            slots,
            deleted_count,
        )
        return jsonify(
            {
                "message": (
                    f"Successfully cancelled {deleted_count} "
                    f"time slots on {date}"
                ),
                "cancelled_slots": list(slots),
            }
        )

    except Exception as e:  # noqa: BLE001
        logger.exception("取消预约时发生异常: {}", e)
        return fail("Internal server error", 500)


@bp.route("/bookings", methods=["GET"])
def get_bookings():
    """获取指定日期的预约信息"""
    instrument = request.args.get("instrument") or "a_instrument"
    date = request.args.get("date")

    if not date:
        logger.warning("获取预约信息失败 - 未提供 date 参数")
        return fail("Date parameter is required")

    logger.debug("查询预约信息 | 仪器: {} | 日期: {}", instrument, date)

    search_by_date_result = db_api.search_booking_by_date(instrument, date)
    if not search_by_date_result:
        return jsonify({"booking": ""}), 200

    bookings_dict = {
        slot["time_slot_id"]: {
            "user_name": slot["user_name"],
            "color": slot.get("color", "#ffffff"),
        }
        for slot in search_by_date_result
    }

    logger.debug(
        "预约查询结果 | 仪器: %s | 日期: %s | 共 %d 条",
        instrument,
        date,
        len(bookings_dict),
    )
    return jsonify({"bookings": bookings_dict})


@bp.route("/bookings_user", methods=["GET"])
@jwt_required()
def get_user_bookings():
    """获取当前用户在指定日期的预约"""
    try:
        date = request.args.get("date")
        instrument = request.args.get("instrument")

        if not date or not instrument:
            return fail("Date and instrument parameters are required")

        current_user_name = get_jwt_identity()
        user = db_api.search_user_by_name(current_user_name)
        if not user:
            logger.warning("查询个人预约失败 - 用户 [{}] 不存在", current_user_name)
            return fail("User not found", 404)

        user_bookings = db_api.search_booking_by_user_and_date(user["id"], date)
        times = [slot["time_slot_id"] for slot in user_bookings]

        logger.debug(
            "用户 [%s] 查询个人预约 | 仪器: %s | 日期: %s | 结果: %s",
            current_user_name,
            instrument,
            date,
            times,
        )
        return jsonify(times)

    except Exception as e:  # noqa: BLE001
        logger.exception("获取用户预约信息时发生异常: {}", e)
        return fail("Internal server error", 500)


@bp.route("/bookings/users", methods=["GET"])
@jwt_required()
def get_booking_users_by_range():
    """查询某仪器在日期范围内预约过的去重用户名与颜色。"""
    instrument = request.args.get("instrument") or "a_instrument"
    start = request.args.get("start")
    end = request.args.get("end")

    if not start or not end:
        logger.warning("查询预约用户失败 - 缺少参数: start=%s, end=%s", start, end)
        return fail("start and end parameters are required")

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError:
        logger.warning("查询预约用户失败 - 日期格式错误: start=%s, end=%s", start, end)
        return fail("Invalid date format, expected YYYY-MM-DD")

    if start_date > end_date:
        logger.warning("查询预约用户失败 - start > end: %s > %s", start, end)
        return fail("start must not be later than end")

    if (end_date - start_date).days > 366:
        logger.warning("查询预约用户失败 - 跨度超限: %s ~ %s", start, end)
        return fail("Date range exceeds 366 days")

    try:
        users = db_api.search_booking_users_by_range(instrument, start, end)
        logger.debug(
            "查询预约用户 | 仪器: %s | 范围: %s~%s | 共 %d 人",
            instrument,
            start,
            end,
            len(users),
        )
        return jsonify({"users": users})
    except Exception as e:  # noqa: BLE001
        logger.error("查询预约用户时发生异常: %s", e, exc_info=True)
        return fail("Internal server error", 500)
