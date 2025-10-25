import hiwonder.ActionGroupControl as AGC

import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller

AGC.runActionGroup('go_forward_one_step', times=2, with_stand=True)                         
# 第二个参数为运行动作次数，默认1, 当为0时表示循环运行， 第三个参数表示最后是否以立正姿态收步

threading.Thread(target=AGC.runActionGroup, args=('go_forward', 0, True)).start()  
# 运行动作函数是阻塞式的，如果要循环运行一段时间后停止，请用线程来开启
time.sleep(3)
AGC.stopActionGroup()  # 前进3秒后停止

AGC.runActionGroup('back_one_step') #向后
AGC.runActionGroup('left_move') #向左
AGC.runActionGroup('right_move') #向右

board = rrc.Board()
ctl = Controller(board)

ctl.set_pwm_servo_pulse(1, 1700, 500) # 上下转头
ctl.set_pwm_servo_pulse(2, 1400, 500) # 左右转头

# 三个参数：

## servo_id: 要驱动的舵机id(the servo id needed to be driven)

## pulse: 舵机目标位置(servo target position)

## use_time: 转动需要的时间(the time needed to rotate)