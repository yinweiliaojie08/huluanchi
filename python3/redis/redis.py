from flask import Flask, jsonify,request
import redis
import javaobj
import logging
import sys

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='[Redis] %(asctime)s %(levelname)s %(message)s',
    stream=sys.stdout
)

REDIS_CONFIG_QQJ = {
    "host": "192.168.10.55",
    "port": 16379,
    "password": "Hefa2016",
    "db": 0,
    "socket_timeout": 10,
    "socket_connect_timeout": 10
}
REDIS_CONFIG_DLYS = {
    "host": "192.168.10.155",
    "port": 16379,
    "password": "Hefa2016",
    "db": 0,
    "socket_timeout": 10,
    "socket_connect_timeout": 5
}

rdb_qqj = redis.Redis(**REDIS_CONFIG_QQJ)
rdb_dlys = redis.Redis(**REDIS_CONFIG_DLYS)

def check_auth():
    username = request.args.get("username")
    password = request.args.get("password")
    return username == "admin" and password == "123456"

def unauthorized():
    return jsonify({"error": "Unauthorized"}), 401

def get_qqj_access_token(key):
    """从 Redis 获取并反序列化字符串"""
    try:
        rdb_qqj.ping()
        val = rdb_qqj.get(key)
        if val is None:
            raise KeyError(f"key 不存在: {key}")
        obj = javaobj.loads(val)  # 固定是字符串
        return str(obj)
    except redis.exceptions.TimeoutError:
        logging.error("Redis 请求超时")
        raise
    except Exception as e:
        logging.error(f"获取或反序列化失败: {e}")
        raise

def get_dlys_access_token(key):
    """从 Redis 获取并反序列化字符串"""
    try:
        rdb_dlys.ping()
        val = rdb_dlys.get(key)
        if val is None:
            raise KeyError(f"key 不存在: {key}")
        obj = javaobj.loads(val)  # 固定是字符串
        return str(obj)
    except redis.exceptions.TimeoutError:
        logging.error("Redis 请求超时")
        raise
    except Exception as e:
        logging.error(f"获取或反序列化失败: {e}")
        raise


@app.route("/get_qqj_token", methods=["GET"])
def get_qqj_token():
    # 从 URL 参数获取用户名和密码
    if not check_auth():
        return unauthorized()
    """API 接口：获取 access_token"""
    key = "wx846c5df7669403ae:basic_token"
    try:
        token = get_qqj_access_token(key)
        return jsonify({"access_token": token})
    except KeyError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_dlys_token", methods=["GET"])
def get_dlys_token():
    if not check_auth():
        return unauthorized()
    """API 接口：获取 access_token"""
    key = "wx846c5df7669403ae:basic_to"
    try:
        token = get_dlys_access_token(key)
        return jsonify({"access_token": token})
    except KeyError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 启动 Web 服务
    app.run(host="0.0.0.0", port=5000, debug=False)

