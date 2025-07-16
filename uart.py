import serial
import time

# 配置参数
PORT_A = 'COM3'   # PortA的串口号 (发送端)
PORT_B = 'COM6'   # PortB的串口号 (接收端)
BAUD_RATE = 115200
TEST_MESSAGE = b'Hello from PortA to PortB!\n'

# 初始化两个串口
try:
    # 初始化PortA (发送端)
    ser_a = serial.Serial(
        port=PORT_A,
        baudrate=BAUD_RATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )
    
    # 初始化PortB (接收端)
    ser_b = serial.Serial(
        port=PORT_B,
        baudrate=BAUD_RATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )
    
    print(f"已打开串口: {ser_a.port} (发送端) 和 {ser_b.port} (接收端)")

    # 从PortA发送测试消息
    print(f"从PortA发送: {TEST_MESSAGE.decode().strip()}")
    ser_a.write(TEST_MESSAGE)
    
    # 在PortB接收数据
    print("在PortB等待接收数据...")
    start_time = time.time()
    timeout = 5  # 5秒超时
    
    while time.time() - start_time < timeout:
        data = ser_b.readline()
        if data:
            print(f"PortB收到: {data.decode().strip()}")
            break
        time.sleep(0.1)  # 短暂等待
    else:
        print("错误: 未在PortB收到数据!")
    
except serial.SerialException as e:
    print(f"串口错误: {e}")
except Exception as e:
    print(f"发生错误: {e}")
finally:
    # 确保关闭所有串口
    if 'ser_a' in locals() and ser_a.is_open:
        ser_a.close()
        print(f"已关闭 {PORT_A}")
    if 'ser_b' in locals() and ser_b.is_open:
        ser_b.close()
        print(f"已关闭 {PORT_B}")