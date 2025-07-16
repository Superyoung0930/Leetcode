import serial
import time
import struct

class HCP1020Controller:
    def __init__(self, port, slave_id=1, baudrate=9600):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1
        )
        self.slave_id = slave_id
    
    def _calculate_crc(self, data):
        # MODBUS CRC16计算实现
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc.to_bytes(2, 'little')
    
    def _send_modbus_command(self, function_code, register, values=None, value=None):
        if function_code == 0x06:  # 写单个寄存器
            frame = struct.pack('>BBHH', 
                self.slave_id, 
                function_code, 
                register, 
                value
            )
        elif function_code == 0x03:  # 读寄存器
            frame = struct.pack('>BBHH', 
                self.slave_id, 
                function_code, 
                register, 
                1  # 读取长度
            )
        elif function_code == 0x10:  # 写多个寄存器
            byte_count = len(values) * 2
            data_part = b''.join([struct.pack('>H', v) for v in values])
            frame = struct.pack('>BBHHB',
                self.slave_id,
                function_code,
                register,
                len(values),  # 寄存器数量
                byte_count
            ) + data_part
    
        crc = self._calculate_crc(frame)
        self.ser.write(frame + crc)
        time.sleep(0.1)
        return self.ser.read_all()
    
    
    # 电压控制 (0x03寄存器)
    def set_voltage(self, volts):
        reg_value = int(volts * 100)  # 转换为10mV单位
        return self._send_modbus_command(0x06, 0x0003, reg_value)
    
    # 电流控制 (0x04寄存器)
    def set_current(self, amps):
        reg_value = int(amps * 1000)  # 转换为1mA单位
        return self._send_modbus_command(0x06, 0x0004, reg_value)
    
    # 输出开关控制 (0x05寄存器位0)
    def set_output(self, state):
        # state: True=开启, False=关闭
        value = 0x0001 if state else 0x0000
        return self._send_modbus_command(0x06, 0x0005, value)
    
    #设定输出电压，电流，输出开命令
    def set_voltage_current_output(self, volts, amps, output_state):
        # 将物理值转换为寄存器值
        voltage_reg = int(volts * 100)  # 电压单位：10mV
        current_reg = int(amps * 1000)  # 电流单位：1mA
        output_reg = 0x0001 if output_state else 0x0000
        # 构造数据部分（电压 + 电流 + 输出状态）
        data_values = [voltage_reg, current_reg, output_reg]
        # 调用通用发送函数（需要扩展_send_modbus_command支持功能码0x10）
        return self._send_modbus_command(
            function_code=0x10,
            register=0x0003,  # 起始寄存器地址
            values=data_values  # 要写入的值列表
        )
    
    def set_protection_values(self, ovp_volts, ocp_amps):
        # 将物理值转换为寄存器值
        ovp_reg = int(ovp_volts * 100)  # OVP单位：10mV (0x07D0=2000 → 20.00V)
        ocp_reg = int(ocp_amps * 1000)  # OCP单位：1mA (0x0C80=3200 → 3.200A)
        # 调用通用发送函数（使用功能码0x10写多个寄存器）
        return self._send_modbus_command(
            function_code=0x10,
            register=0x0006,  # OVP寄存器起始地址
            values=[ovp_reg, ocp_reg]  # 要写入的值列表[OVP, OCP]
        )

    # 过压保护设置 (0x06寄存器)
    def set_ovp(self, volts):
        reg_value = int(volts * 100)  # 转换为10mV单位
        return self._send_modbus_command(0x06, 0x0006, reg_value)
    
    # 过流保护设置 (0x07寄存器)
    def set_ocp(self, amps):
        reg_value = int(amps * 1000)  # 转换为1mA单位
        return self._send_modbus_command(0x06, 0x0007, reg_value)
    
    #设置输出开，过压保护功能开，过流保护功能开
    def set_output_protections(self, output_on=True, ovp_enable=True, ocp_enable=True):
        # 根据状态位说明构造控制字
        control_word = 0x0000
        if output_on:
            control_word |= 0x0001  # 位0：输出开关
        if ovp_enable:
            control_word |= 0x0008  # 位3：OVP功能
        if ocp_enable:
            control_word |= 0x0010  # 位4：OCP功能
        # 调用通用发送函数（使用功能码0x06写单个寄存器）
        return self._send_modbus_command(
            function_code=0x06,
            register=0x0005,  # 控制寄存器地址
            value=control_word
        )

    #查询设置电压，电流，状态 
    def query_settings(self):
        # 发送读取命令（起始地址0x0003，读取3个寄存器）
        response = self._send_modbus_command(
            function_code=0x03,
            register=0x0003,  # 起始寄存器地址
            read_length=3     # 读取3个寄存器（电压、电流、状态）
        )
        # 解析响应数据（示例响应：11 03 06 01 F4 04 B0 00 01 9D A6）
        if response and len(response) >= 9:
            # 提取数据部分（跳过地址、功能码和字节计数）
            data = response[3:-2]  # 去除头尾的协议字段和CRC
            # 解析电压（寄存器0x03）
            voltage_reg = struct.unpack('>H', data[0:2])[0]
            voltage = voltage_reg / 100.0  # 转换为V（10mV单位）
            # 解析电流（寄存器0x04）
            current_reg = struct.unpack('>H', data[2:4])[0]
            current = current_reg / 1000.0  # 转换为A（1mA单位）
            # 解析状态（寄存器0x05）
            status_reg = struct.unpack('>H', data[4:6])[0]
            return {
                'voltage': voltage,
                'current': current,
                'output_on': bool(status_reg & 0x0001),  # 位0：输出状态
                'cv_mode': bool(status_reg & 0x0002),    # 位1：恒压模式
                'cc_mode': bool(status_reg & 0x0004)     # 位2：恒流模式
            }
        return None

    # 读取实际输出电压 (0x00寄存器)
    def read_voltage(self):
        response = self._send_modbus_command(0x03, 0x0000)
        if len(response) >= 7:
            return struct.unpack('>H', response[3:5])[0] / 100.0  # 转换为V
        return None
    
    # 读取实际输出电流 (0x01寄存器)
    def read_current(self):
        response = self._send_modbus_command(0x03, 0x0001)
        if len(response) >= 7:
            return struct.unpack('>H', response[3:5])[0] / 1000.0  # 转换为A
        return None
    
    # 读取电源状态 (0x02寄存器)
    def read_status(self):
        response = self._send_modbus_command(0x03, 0x0002)
        if len(response) >= 7:
            status_bits = struct.unpack('>H', response[3:5])[0]
            return {
                'output_on': bool(status_bits & 0x01),
                'cv_mode': bool(status_bits & 0x02),
                'cc_mode': bool(status_bits & 0x04),
                'ovp_tripped': bool(status_bits & 0x08),
                'ocp_tripped': bool(status_bits & 0x10),
                'otp_tripped': bool(status_bits & 0x20)
            }
        return None

    def query_actual_values(self):
        # 发送读取命令（起始地址0x0000，读取3个寄存器）
        response = self._send_modbus_command(
            function_code=0x03,
            register=0x0000,  # 起始寄存器地址
            read_length=3      # 读取3个寄存器（电压、电流、状态）
        )
        # 解析响应数据（示例响应：11 03 06 01 F3 00 00 03 XX XX）
        if response and len(response) >= 9:
            # 提取数据部分（跳过地址、功能码和字节计数）
            data = response[3:-2]  # 去除头尾的协议字段和CRC
            # 解析实际电压（寄存器0x00）
            voltage_reg = struct.unpack('>H', data[0:2])[0]
            actual_voltage = voltage_reg / 100.0  # 转换为V（10mV单位）
            # 解析实际电流（寄存器0x01）
            current_reg = struct.unpack('>H', data[2:4])[0]
            actual_current = current_reg / 1000.0  # 转换为A（1mA单位）
           # 解析输出状态（寄存器0x02）
            status_reg = struct.unpack('>H', data[4:6])[0]
            return {
                'voltage': actual_voltage,
                'current': actual_current,
                'output_status': {
                    'output_on': bool(status_reg & 0x0001),  # 位0：输出状态
                    'cv_mode': bool(status_reg & 0x0002),    # 位1：恒压模式
                    'cc_mode': bool(status_reg & 0x0004),    # 位2：恒流模式
                    'ovp_tripped': bool(status_reg & 0x0008),# 位3：OVP触发
                    'ocp_tripped': bool(status_reg & 0x0010) # 位4：OCP触发
                }
            }
        return None

    # 恒功率模式设置
    def set_constant_power(self, watts):
        # 设置线阻补偿 (0x30寄存器)
        self._send_modbus_command(0x06, 0x0030, 100)  # 示例值
        
        # 设置负载阻值 (0x31寄存器)
        self._send_modbus_command(0x06, 0x0031, 500)  # 示例值
        
        # 启用恒功率模式 (0x32寄存器)
        self._send_modbus_command(0x06, 0x0032, 0x0001)
        
        # 设置功率值 (0x34寄存器)
        reg_value = int(watts * 100)  # 转换为10mW单位
        return self._send_modbus_command(0x06, 0x0034, reg_value)
    
    # 定时输出序列
    def execute_sequence(self, sequence):
        """ 执行测试序列
        sequence格式: [(电压, 电流, 持续时间), ...]
        """
        for volt, curr, duration in sequence:
            self.set_voltage(volt)
            self.set_current(curr)
            self.set_output(True)
            time.sleep(duration)
        self.set_output(False)
    # 清除保护状态
    def clear_protections(self):
        return self._send_modbus_command(0x06, 0x0005, 0x0040)
    
    # 键盘锁定
    def lock_keyboard(self, lock=True):
        value = 0x4000 if lock else 0x0000
        return self._send_modbus_command(0x06, 0x0005, value)
# 自动化测试脚本示例
psu = HCP1020Controller('/dev/ttyUSB0', slave_id=1)

try:
    # 设置保护参数
    psu.set_ovp(12.0)  # 12V过压保护
    psu.set_ocp(2.0)   # 2A过流保护
    
    # 执行测试序列
    test_sequence = [
        (3.3, 0.5, 5),   # 3.3V@0.5A 持续5秒
        (5.0, 1.0, 10),   # 5.0V@1.0A 持续10秒
        (12.0, 0.2, 3)    # 12V@0.2A 持续3秒
    ]
    psu.execute_sequence(test_sequence)
    
    # 读取测试结果
    final_voltage = psu.read_voltage()
    final_current = psu.read_current()
    print(f"最终读数: {final_voltage}V, {final_current}A")
    
finally:
    psu.set_output(False)  # 确保测试结束后关闭输出