#需安装Flask和gunicorn
from flask import Flask, jsonify, request
import hiwonder.ActionGroupControl as AGC
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller

# 初始化Flask应用
app = Flask(__name__)
board = rrc.Board()
ctl = Controller(board)


# 创建一个API端点来执行动作
# 可以通过访问 http://<树莓派IP>:5000/run_action/stand 来让机器人站立
@app.route('/run_action/<string:action_name>', methods=['GET'])
def run_robot_action(action_name):
    try:
        print(f"接收到指令，执行动作: {action_name}")
        # 直接调用您SDK中的函数
        # 注意：这里的路径需要是机器人的实际路径，如果SDK默认值正确则无需修改
        AGC.runAction(action_name)
        return jsonify({"status": "success", "action": action_name})
    except Exception as e:
        print(f"执行动作失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/turn_head', methods=['POST'])
def turn_head():
    req_data = request.get_json()
    servo_id = req_data.get('servo_id')
    pulse = req_data.get('pulse')
    ctl.set_pwm_servo_pulse(servo_id, pulse, 500)
    return jsonify({"status": "success", "servo_id": servo_id, "pulse": pulse})


if __name__ == '__main__':
    # 监听所有网络接口，这样局域网内的设备才能访问
    app.run(host='0.0.0.0', port=5000)