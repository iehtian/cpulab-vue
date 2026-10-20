"""空间管理路由：添加/更新空间、获取全部空间。"""

from flask import Blueprint, jsonify, request

import database as db_api
from log_config import logger
from utils.helpers import fail

bp = Blueprint("spaces", __name__)


@bp.route("/space/add", methods=["POST"])
def add_space_api():
    """添加或更新空间信息"""
    try:
        data = request.get_json()
        name = data.get("name")

        if not name:
            return fail("Space name is required")

        db_api.add_space(name)
        logger.info("空间信息已添加| 名称: {}", name)
        return jsonify({"message": "Space information added successfully"})

    except Exception as e:  # noqa: BLE001
        logger.exception("空间信息添加/更新时发生异常: {}", e)
        return fail("Internal server error", 500)


@bp.route("/space/delete/<int:space_id>", methods=["DELETE"])
def delete_space_api(space_id):
    """根据空间 ID 删除空间信息"""
    try:
        db_api.delete_space_by_id(space_id)
        logger.info("空间信息已删除 | ID: {}", space_id)
        return jsonify({"message": "Space information deleted successfully"})

    except Exception as e:  # noqa: BLE001
        logger.exception("空间信息删除时发生异常: {}", e)
        return fail("Internal server error", 500)


@bp.route("/space/all", methods=["GET"])
def get_all_spaces_api():
    """获取所有空间信息"""
    try:
        spaces = db_api.get_all_spaces()
        logger.debug("查询所有空间信息 | 共 {} 条", len(spaces))
        return jsonify({"spaces": spaces})

    except Exception as e:  # noqa: BLE001
        logger.exception("查询所有空间信息时发生异常: {}", e)
        return fail("Internal server error", 500)
