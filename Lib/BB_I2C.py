import Adafruit_GPIO.I2C as twi


class I2C:
    def __init__(self,bus_num,dev_addr):
        self.bus = twi.Device(dev_addr,bus_num)

    def write8(self,write_addr,data):
        self.bus.write8(write_addr,data)
    def write16(self,write_addr,data):
        upper = (data>>8) & 0xFF
        lower = (data) & 0xFF
        self.bus.write8(write_addr,higher)
        self.bus.write8(write_addr+1,lower)
    def readU8(self, addr):
        return self.bus.readU8(addr)
    def readU16(self,addr):
        return self.bus.readU16(addr)
        


class TCS3475:
    def __init__(self,i2c_obj):
        self.bus = i2c_obj
        self.bus.write8(0x80 | 0x00, 0x03)

    def readRGB(self):
        clear_l = self.bus.readU8(0x80|0x14)
        clear_h = self.bus.readU8(0x80|0x15)
        r_l = self.bus.readU8(0x80 | 0x16)
        r_h = self.bus.readU8(0x80 | 0x17)
        g_l = self.bus.readU8(0x80 | 0x18)
        g_h = self.bus.readU8(0x80 | 0x19)
        b_l = self.bus.readU8(0x80 | 0x1A)
        b_h = self.bus.readU8(0x80 | 0x1B)
        clear = (clear_h << 8) | clear_l
        r     = (r_h << 8) | r_l
        g     = (g_h << 8) | g_l
        b     = (b_h << 8) | b_l
        r = (float(r) / float(clear))* 255.0
        g = (float(g) / float(clear))* 255.0
        b = (float(b) / float(clear))* 255.0

        return (r,g,b)

    def cleanup(self):
        self.bus.cleanup()


 


ACCEL_OUT = 0x3B
GYRO_OUT = 0x43
TEMP_OUT = 0x41
EXT_SENS_DATA_00 = 0x49
ACCEL_CONFIG = 0x1C
ACCEL_FS_SEL_2G = 0x00
ACCEL_FS_SEL_4G = 0x08
ACCEL_FS_SEL_8G = 0x10
ACCEL_FS_SEL_16G = 0x18
GYRO_CONFIG = 0x1B
GYRO_FS_SEL_250DPS = 0x00
GYRO_FS_SEL_500DPS = 0x08
GYRO_FS_SEL_1000DPS = 0x10
GYRO_FS_SEL_2000DPS = 0x18
ACCEL_CONFIG2 = 0x1D
ACCEL_DLPF_184 = 0x01
ACCEL_DLPF_92 = 0x02
ACCEL_DLPF_41 = 0x03
ACCEL_DLPF_20 = 0x04
ACCEL_DLPF_10 = 0x05
ACCEL_DLPF_5 = 0x06
CONFIG = 0x1A
GYRO_DLPF_184 = 0x01
GYRO_DLPF_92 = 0x02
GYRO_DLPF_41 = 0x03
GYRO_DLPF_20 = 0x04
GYRO_DLPF_10 = 0x05
GYRO_DLPF_5 = 0x06
SMPDIV = 0x19
INT_PIN_CFG = 0x37
INT_ENABLE = 0x38
INT_DISABLE = 0x00
INT_PULSE_50US = 0x00
INT_WOM_EN = 0x40
INT_RAW_RDY_EN = 0x01
PWR_MGMNT_1 = 0x6B
PWR_CYCLE = 0x20
PWR_RESET = 0x80
CLOCK_SEL_PLL = 0x01
PWR_MGMNT_2 = 0x6C
SEN_ENABLE = 0x00
DIS_GYRO = 0x07
USER_CTRL = 0x6A
I2C_MST_EN = 0x20
I2C_MST_CLK = 0x0D
I2C_MST_CTRL = 0x24
I2C_SLV0_ADDR = 0x25
I2C_SLV0_REG = 0x26
I2C_SLV0_DO = 0x63
I2C_SLV0_CTRL = 0x27
I2C_SLV0_EN = 0x80
I2C_READ_FLAG = 0x80
MOT_DETECT_CTRL = 0x69
ACCEL_INTEL_EN = 0x80
ACCEL_INTEL_MODE = 0x40
LP_ACCEL_ODR = 0x1E
WOM_THR = 0x1F
WHO_AM_I = 0x75
FIFO_EN = 0x23
FIFO_TEMP = 0x80
FIFO_GYRO = 0x70
FIFO_ACCEL = 0x08
FIFO_MAG = 0x01
FIFO_COUNT = 0x72
FIFO_READ = 0x74
AK8963_I2C_ADDR = 0x0C
AK8963_HXL = 0x03 
AK8963_CNTL1 = 0x0A
AK8963_PWR_DOWN = 0x00
AK8963_CNT_MEAS1 = 0x12
K8963_CNT_MEAS2 = 0x16
AK8963_FUSE_ROM = 0x0F
AK8963_CNTL2 = 0x0B
AK8963_RESET = 0x01
AK8963_ASA = 0x10
AK8963_WHO_AM_I = 0x00

import time



class MPU9250:
    def __init__(self, bus):
        self.i2c = bus
        if(not self.write_and_check(PWR_MGMNT_1, CLOCK_SEL_PLL)): return -1
        if(not self.write_and_check(I2C_MST_CTRL, I2C_MST_CLK)): return -1
        self.i2c.write8(PWR_MGMNT_1,PWR_RESET)

        time.sleep(1)

        self.i2c.write8(PWR_MGMNT_1, CLOCK_SEL_PLL)
        self.i2c.write8(PWR_MGMNT_2, SEN_ENABLE)
        self.i2c.write8(ACCEL_CONFIG, ACCEL_FS_SEL_16G)
        self.i2c.write8(GYRO_CONFIG, GYRO_FS_SEL_2000DPS)
        self.i2c.write8(ACCEL_CONFIG2, ACCEL_DLPF_184)
        self.i2c.write8(CONFIG, GYRO_DLPF_184)
        self.i2c.write8(CONFIG, GYRO_DLPF_184)


    def write_and_check(self, addr, data):
        self.i2c.write8(addr,data)
        return self.i2c.readU8(addr)==data

    def get_data(self):
        accel = self.i2c.readU16(ACCEL_OUT)
        gyro  =  self.i2c.readU16(GYRO_OUT)
        temp  =  self.i2c.readU16(TEMP_OUT)
        return (accel,gyro,temp)


