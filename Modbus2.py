from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer
import serial
import time
import logging
import re

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
log = logging.getLogger(__name__)

class PowerSupplyController:
    """通过Modbus RTU协议控制电源的类"""
    
    def __init__(self, port, baudrate=9600, data_bits=8, parity='N', stop_bits=1, timeout=1):
        """初始化Modbus RTU连接"""
        self.port = port
        self.baudrate = baudrate
        self.data_bits = data_bits
        self.parity = parity
        self.stop_bits = stop_bits
        self.timeout = timeout
        self.client = None
        self.connected = False
        
    def connect(self):
        """连接到电源"""
        try:
            self.client = ModbusClient(
                method='rtu',
                port=self.port,
                baudrate=self.baudrate,
                parity=self.parity,
                stopbits=self.stop_bits,
                bytesize=self.data_bits,
                timeout=self.timeout
            )
            self.connected = self.client.connect()
            if self.connected:
                log.info(f"成功连接到电源，端口: {self.port}，波特率: {self.baudrate}")
            else:
                log.error("无法连接到电源，请检查串口设置和连接")
            return self.connected
        except Exception as e:
            log.error(f"连接错误: {str(e)}")
            return False
    
    def disconnect(self):
        """断开与电源的连接"""
        if self.connected and self.client:
            self.client.close()
            self.connected = False
            log.info("已断开与电源的连接")
    
    def send_raw_command(self, hex_command, unit=1):
        """发送原始十六进制Modbus命令"""
        if not self.connected:
            log.error("未连接到电源，无法发送命令")
            return None
            
        try:
            # 解析十六进制命令
            command = bytes.fromhex(hex_command.replace(' ', ''))
            
            # 根据功能码选择操作
            function_code = command[1]
            if function_code == 0x03:  # 读保持寄存器
                address = (command[2] << 8) | command[3]
                count = (command[4] << 8) | command[5]
                result = self.client.read_holding_registers(address, count, unit=unit)
            elif function_code == 0x06:  # 写单个寄存器
                address = (command[2] << 8) | command[3]
                value = (command[4] << 8) | command[5]
                result = self.client.write_single_register(address, value, unit=unit)
            elif function_code == 0x10:  # 写多个寄存器
                address = (command[2] << 8) | command[3]
                count = (command[4] << 8) | command[5]
                byte_count = command[6]
                values = [(command[i+7] << 8) | command[i+8] for i in range(0, byte_count, 2)]
                result = self.client.write_multiple_registers(address, values, unit=unit)
            else:
                log.warning(f"不支持的功能码: {function_code}")
                return None
                
            if not result.isError():
                log.info(f"命令发送成功: {hex_command}")
                # 对于读命令，返回寄存器值
                if function_code == 0x03:
                    return result.registers
                return True
            else:
                log.error(f"命令执行错误: {result}，命令: {hex_command}")
                return None
        except Exception as e:
            log.error(f"发送命令异常: {str(e)}，命令: {hex_command}")
            return None
    
    # 电源控制的具体功能（基于提供的示例）
    def set_voltage(self, voltage, unit=1):
        """设置输出电压"""
        # 示例1: 11 06 00 03 01 F4 (5.0V)
        # 寄存器地址0x0003，值0x01F4=500，假设精度0.01V
        hex_value = int(voltage * 100)
        hex_command = f"11 06 00 03 {hex_value:04X}"
        return self.send_raw_command(hex_command, unit)
    
    def set_current(self, current, unit=1):
        """设置输出电流"""
        # 示例2: 11 06 00 04 04 B0 (1.2A)
        # 寄存器地址0x0004，值0x04B0=1200，假设精度0.001A
        hex_value = int(current * 1000)
        hex_command = f"11 06 00 04 {hex_value:04X}"
        return self.send_raw_command(hex_command, unit)
    
    def enable_output(self, enable=True, unit=1):
        """启用或禁用电源输出"""
        # 示例3: 11 06 00 05 00 01 (开输出)
        # 寄存器地址0x0005，值0x0001=开，0x0000=关
        value = 0x0001 if enable else 0x0000
        hex_command = f"11 06 00 05 {value:04X}"
        return self.send_raw_command(hex_command, unit)
    
    def set_voltage_current_output(self, voltage, current, enable=True, unit=1):
        """设定输出电压、电流并控制输出状态"""
        # 示例4: 11 10 00 03 00 03 06 01 F4 04 B0 00 01
        # 写多个寄存器，地址0x0003开始，3个寄存器
        voltage_reg = int(voltage * 100)
        current_reg = int(current * 1000)
        output_reg = 0x0001 if enable else 0x0000
        values = [voltage_reg, current_reg, output_reg]
        hex_command = "11 10 00 03 00 03 06"
        for val in values:
            hex_command += f" {val:04X}"
        return self.send_raw_command(hex_command, unit)
    
    def set_ovp_ocp(self, ovp_voltage, ocp_current, unit=1):
        """设定过压保护值和过流保护值"""
        # 示例5: 11 10 00 06 00 02 04 07 D0 0C 80
        # 写多个寄存器，地址0x0006开始，2个寄存器
        ovp_reg = int(ovp_voltage * 100)
        ocp_reg = int(ocp_current * 1000)
        values = [ovp_reg, ocp_reg]
        hex_command = "11 10 00 06 00 02 04"
        for val in values:
            hex_command += f" {val:04X}"
        return self.send_raw_command(hex_command, unit)
    
    def query_voltage_current_status(self, unit=1):
        """查询设置电压、电流和状态"""
        # 示例7: 11 03 00 03 00 03
        # 读3个寄存器，地址0x0003开始
        hex_command = "11 03 00 03 00 03"
        registers = self.send_raw_command(hex_command, unit)
        if registers:
            voltage = registers[0] / 100  # 假设精度0.01V
            current = registers[1] / 1000  # 假设精度0.001A
            status = "ON" if registers[2] == 1 else "OFF"
            return {"voltage": voltage, "current": current, "status": status}
        return None
    
    def query_voltage_display(self, unit=1):
        """查询电压显示值"""
        # 示例8: 11 03 00 00 00 01
        # 读1个寄存器，地址0x0000
        hex_command = "11 03 00 00 00 01"
        registers = self.send_raw_command(hex_command, unit)
        if registers:
            return registers[0] / 100  # 假设精度0.01V
        return None
    
    def query_current_display(self, unit=1):
        """查询电流显示值"""
        # 示例9: 11 03 00 01 00 01
        # 读1个寄存器，地址0x0001
        hex_command = "11 03 00 01 00 01"
        registers = self.send_raw_command(hex_command, unit)
        if registers:
            return registers[0] / 1000  # 假设精度0.001A
        return None
    
    def query_output_status(self, unit=1):
        """查询输出状态"""
        # 示例10: 11 03 00 02 00 01
        # 读1个寄存器，地址0x0002
        hex_command = "11 03 00 02 00 01"
        registers = self.send_raw_command(hex_command, unit)
        if registers:
            return "ON" if registers[0] == 1 else "OFF"
        return None
    
    def query_voltage_current_status_display(self, unit=1):
        """查询电压、电流和输出状态显示值"""
        # 示例11: 11 03 00 00 00 03
        # 读3个寄存器，地址0x0000开始
        hex_command = "11 03 00 00 00 03"
        registers = self.send_raw_command(hex_command, unit)
        if registers:
            voltage = registers[0] / 100  # 假设精度0.01V
            current = registers[1] / 1000  # 假设精度0.001A
            status = "ON" if registers[2] == 1 else "OFF"
            return {"voltage": voltage, "current": current, "status": status}
        return None

# 批量发送命令示例
def batch_send_commands(controller, commands, unit=1):
    """批量发送命令"""
    results = []
    for cmd in commands:
        # 解析命令格式: 1=1|1000|1|设置电压5.0V|11 06 00 03 01 F4
        match = re.match(r'(\d+)=(\d+)\|(\d+)\|(\d+)\|(.*)\|(.*)', cmd)
        if match:
            idx, slave_addr, baudrate, data_bits, desc, hex_cmd = match.groups()
            # 注意：示例中的波特率1000可能是笔误，通常为9600、115200等
            # 此处强制使用控制器的波特率，如需动态设置可修改
            log.info(f"执行命令 {idx}: {desc}")
            result = controller.send_raw_command(hex_cmd, int(slave_addr))
            results.append((desc, result))
            time.sleep(0.5)  # 命令间隔
    return results

# 使用示例
if __name__ == "__main__":
    # 根据实际情况修改串口参数
    power_supply = PowerSupplyController(
        port='COM3',  # Windows串口，Linux/Mac为'/dev/ttyUSB0'
        baudrate=9600,
        data_bits=8,
        parity='N',
        stop_bits=1
    )
    
    try:
        # 连接到电源
        if power_supply.connect():
            # 示例1: 设置电压5.0V
            power_supply.set_voltage(5.0)
            time.sleep(0.5)
            
            # 示例2: 设置电流1.2A
            power_supply.set_current(1.2)
            time.sleep(0.5)
            
            # 示例3: 开输出
            power_supply.enable_output(True)
            time.sleep(1)
            
            # 示例7: 查询设置电压、电流和状态
            status = power_supply.query_voltage_current_status()
            if status:
                print(f"当前设置: 电压={status['voltage']}V, 电流={status['current']}A, 状态={status['status']}")
            
            # 示例8-11: 查询显示值
            voltage_display = power_supply.query_voltage_display()
            current_display = power_supply.query_current_display()
            output_status = power_supply.query_output_status()
            print(f"当前显示: 电压={voltage_display}V, 电流={current_display}A, 输出状态={output_status}")
            
            # 示例4: 一次性设置电压、电流并开输出
            power_supply.set_voltage_current_output(5.0, 1.2, True)
            time.sleep(1)
            
            # 示例5: 设置过压保护6.0V，过流保护1.5A
            power_supply.set_ovp_ocp(6.0, 1.5)
            
            # 批量发送命令示例
            batch_commands = [
                "1=1|1000|1|设置电压5.0V|11 06 00 03 01 F4",
                "2=1|1000|1|设置电流1.2A|11 06 00 04 04 B0",
                "3=1|1000|1|开输出|11 06 00 05 00 19",
                "7=1|1000|1|查询设置电压，电流，状态|11 03 00 03 00 03",
                "8=1|1000|1|查询电压显示|11 03 00 00 00 01",
                "9=1|1000|1|查询电流显示|11 03 00 01 00 01",
                "10=1|1000|1|查询输出状态|11 03 00 02 00 1"
            ]
            batch_results = batch_send_commands(power_supply, batch_commands)
            for desc, result in batch_results:
                print(f"命令[{desc}]执行结果: {result}")
            
            # 关输出
            power_supply.enable_output(False)
    finally:
        # 断开连接
        power_supply.disconnect()