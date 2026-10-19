"""杂项路由：健康检查、changelog 文件服务。"""

from pathlib import Path

from flask import Blueprint, jsonify, send_from_directory

from log_config import logger
from utils.helpers import set_cookie_with_defaults

bp = Blueprint("misc", __name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@bp.route("/hello_world", methods=["GET"])
def hello_world():
    logger.info("健康检查接口被访问")
    response = jsonify({"message": "Hello, World!"})
    set_cookie_with_defaults(response, "test_cookie", "test_value")
    return response


# 该 blueprint 注册时不加 url_prefix，路由写完整路径
@bp.route("/api/changelog", methods=["GET"])
def serve_changelog_md():
    """提供 changelog.md 文件"""
    changelog_path = BASE_DIR / "changelog.md"
    if not changelog_path.exists():
        logger.warning("changelog.md 文件不存在: {}", changelog_path)
        return jsonify({"error": "changelog.md not found"}), 404
    return send_from_directory(changelog_path.parent, changelog_path.name)
