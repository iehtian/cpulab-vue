"""Flask 应用入口：组装配置、扩展与各业务路由蓝图。"""

from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from log_config import logger
from routes import auth, bookings, daily_plan, dygx, misc, reagents, spaces, zones

CORS_ORIGINS = [
    "http://localhost:5501",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://localhost:5173",
    "https://127.0.0.1:5173",
]

# 以 /api 为前缀注册的业务蓝图
API_BLUEPRINTS = (auth, bookings, daily_plan, dygx, spaces, zones, reagents)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, supports_credentials=True, origins=CORS_ORIGINS)

    @app.after_request
    def add_cache_headers(response):
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, max-age=0"
            )
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            response.headers["Vary"] = "Authorization, Origin"
        return response

    JWTManager(app)

    for module in API_BLUEPRINTS:
        app.register_blueprint(module.bp, url_prefix="/api")
    # misc 包含 /hello_world 等非 /api 前缀路由，注册时不加前缀
    app.register_blueprint(misc.bp)

    return app


app = create_app()


if __name__ == "__main__":
    import database as db_api

    if db_api.initialize_database():
        logger.info("数据库初始化完成（users/bookings/date_plans），系统已准备好运行")
    else:
        logger.error("数据库初始化失败，请检查错误日志")
    app.run(host="0.0.0.0", port=5000, debug=True)
