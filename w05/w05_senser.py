from gpiozero import OutputDevice, Button
from time import sleep
import hiwonder.ros_robot_controller_sdk as rrc

# 初始化板载蜂鸣器
board = rrc.Board()

# 初始化风扇控制引脚
fanPin1 = OutputDevice(8)  # BCM 8
fanPin2 = OutputDevice(7)  # BCM 7

# 初始化触摸传感器引脚
touch = Button(22)  # BCM 22

# 风扇状态变量
fan_state = False  # False表示关闭，True表示开启
touch_pressed = False  # 触摸传感器是否被按下

# 风扇控制函数
def set_fan(state):
    global fan_state
    fan_state = state
    
    if fan_state:
        # 开启风扇, 顺时针
        print("Turning fan ON")
        fanPin1.on()   # 输出高电平
        fanPin2.off()  # 输出低电平
        # 蜂鸣器提示音
        board.set_buzzer(1900, 0.2, 0.1, 1)  # 较高音调，短促
    else:
        # 关闭风扇
        print("Turning fan OFF")
        fanPin1.off()  # 输出低电平
        fanPin2.off()  # 输出低电平
        # 蜂鸣器提示音
        board.set_buzzer(1200, 0.2, 0.1, 1)  # 较低音调，短促

if __name__ == '__main__':
    try:
        # 初始状态，关闭风扇
        set_fan(False)
        print("Fan control system started. Press touch sensor to toggle fan.")
        
        while True:
            # 检测触摸传感器状态变化
            if touch.is_pressed and not touch_pressed:
                # 触摸传感器刚刚被按下
                touch_pressed = True
                # 切换风扇状态
                set_fan(not fan_state)
                # 添加短暂延时防止重复触发
                sleep(0.5)
            
            # 检测触摸传感器释放
            elif not touch.is_pressed and touch_pressed:
                touch_pressed = False
            
            # 短延时，降低CPU占用
            sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nProgram interrupted. Turning fan off.")
        # 确保程序退出时关闭风扇
        set_fan(False)
    finally:
        # 清理资源
        set_fan(False)
        print("Program terminated.")