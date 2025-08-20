from ..rtmq2.std import *

class rsm(rsm.__class__):
    uart = bit_field(3)
    coproc = bit_field(5)
    spi = bit_field(6)
    gpio = bit_field(7)

rsm = rsm()

ttl = port('ttl')

class dio(ports):
    def __init__(self):
        super().__init__()
        self.dir = port('dir')
        self.inv = port('inv')
        self.pos = port('pos')
        self.neg = port('neg')

dio = dio()

class spi_ctl(port):
    clk_div = bit_field(0,11)
    sdi_ltn = bit_field(12,15)
    pha = bit_field(16)
    pol = bit_field(17)

class spi_cnt(port):
    tot_bit = bit_field(0,9)
    sdo_bit = bit_field(10,19)

class spi(ports):
    def __init__(self, idx, N_SPI_SEG):
        super().__init__(f'spi{idx:02x}')
        self.N_SPI_SEG = N_SPI_SEG
        for i in range(N_SPI_SEG):
            setattr(self,f'&{i:02x}',port(f'&{i:02x}'))
        self.ctl = spi_ctl('ctl')
        self.cnt = spi_cnt('cnt')

    def config(self, pol, pha, sdi_ltn, clk_div):
        self.ctl(pol=pol,pha=pha,sdi_ltn=sdi_ltn,clk_div=clk_div)

    def write(self, dat, bit_cnt):
        for i in range(len(dat)):
            self[self.N_SPI_SEG-1-i](dat[i])
        self.cnt(tot_bit=bit_cnt, sdo_bit=bit_cnt)
    
    @staticmethod
    def wait():
        std.wait(spi=1)
        std.timer(1,us=True,sleep=2)
    
    def wr_5372(self, mod, adr, dat):
        """
        Low level SPI write function for AD5372.
        <mod> is the 2 mode bits, <adr> is the 6 address bits, and <dat> is the 16 data bits.
        For more information, please refer to the datasheet of AD5372.
        """
        buf = bit_concat((mod, 2), (adr, 6), (dat, 16), (0, 8))
        self.write([buf], 24)
    
    def wr_5791(self, rwb, adr, dat):
        """
        Low level SPI write function for AD5791.
        <rwb> is the r/~w bit, 0 for write operation;
        <adr> is the 3 address bits, and <dat> is the 20 data bits.
        For more information, please refer to the datasheet of AD5791.
        """
        buf = bit_concat((rwb, 1), (adr, 3), (dat, 20), (0, 8))
        self.write([buf], 24)
    
    def wr_8563(self, cmd, adr, dat):
        """
        Low level SPI write function for DAC8563.
        <cmd> is the 3 command bits, <adr> is the 3 address bits, and <dat> is the 16 data bits.
        For more information, please refer to the datasheet of DAC8563.
        """
        buf = bit_concat((cmd, 3), (adr, 3), (dat, 16), (0, 8))
        self.write([buf], 24)
    
    def rd_5372(self, adr):
        """
        SPI register readback function for AD5372. Set <adr> according to the datasheet.
        """
        self.wr_5372(0b00, 0b000_101, adr)
        self.wait()
        self.wr_5372(0, 0, 0)
        self.wait()
        return pin(self)()

    def rd_5791(self, adr):
        """
        SPI register readback function for AD5791. Set <adr> according to the datasheet.
        """
        self.wr_5791(1, adr, 0)
        self.wait()
        self.wr_5791(0, 0, 0)
        self.wait()
        return pin(self)()
    
    def dac_5372(self, grp, chn, val, dst="X"):
        """
        Set DAC outputs of AD5372. For definitions of <grp> and <chn>, please refer to the datasheet.
        <dst> is the destination of the write operation:
        'X': to the data register
        'C': to the offset register (calibration)
        'M': to the gain register (calibration)
        <val> is the data to be written, if <dst> is 'X', it's in 2's complement, otherwise it is written as is.
        """
        mod = {"X": 3, "C": 2, "M": 1}[dst]
        if mod == 3:
            if type(val) is not int:
                val = round(val/20*0xffff)
            self.wr_5372(mod, grp*8+chn, val^0x8000)
        else:
            self.wr_5372(mod, grp*8+chn, val)
    
    def dac_5791(self, val):
        """
        Set DAC outputs of AD5791. <val> is in 2's complement.
        """
        if type(val) is not int:
            val = round(val/20*0xfffff)
        self.wr_5791(0, 1, val)
    
    def dac_8563(self, chn, val):
        """
        Set DAC outputs of DAC8563. <val> is in 2's complement.
        """
        if type(val) is not int:
            val = round(val/20*0xffff)
        self.wr_8563(0b011, chn, val^0x8000)

class cou(ports):
    def __init__(self, N_COU):
        super().__init__()
        if type(N_COU) in (tuple,list):
            for i in range(len(N_COU)):
                setattr(self,f'&{i:02x}',(N_COU[i] or port)(f'&{i:02x}'))
        else:
            for i in range(N_COU):
                setattr(self,f'&{i:02x}',port(f'&{i:02x}'))

class cin(ports):
    def __init__(self, N_CIN):
        super().__init__()
        if type(N_CIN) in (tuple,list):
            for i in range(len(N_CIN)):
                setattr(self,f'&{i:02x}',(N_CIN[i] or port)(f'&{i:02x}'))
        else:
            for i in range(N_CIN):
                setattr(self,f'&{i:02x}',port(f'&{i:02x}'))

class ftw(ports):
    def __init__(self, N_DDS):
        super().__init__()
        for i in range(N_DDS):
            setattr(self,f'&{i:02x}',port(f'&{i:02x}'))

amp = port('amp')
pow = port('pow')
ofs = port('ofs')
    
class flex(std.__class__):
    def config(self,N_DIO,N_COU,N_CIN,N_SPI):
        N_SPI_SEG = 16
        N_DDS = 8
        self.core = base_core(
        ["ICF", "ICA", "ICD", "DCF", "DCA", "DCD",
        "NEX", "FRM", "SCP", "TIM", "WCL", "WCH",
        "LED", "FAI", "MAC", "CPR",
        "TTL", "DIO", "CTR", "CSM", "TTS", "TEV",
        "CLR", "ENA", "OPT", "FTW", "POW", "AMP", "OFS", "SIG",
        "IOU", "COU", "IIN", "CIN"] + \
        [f"SPI{n:02X}" for n in range(N_SPI)], ["ICA", "DCA"],
        {"NEX": [None]*32 + ["ADR", "BCE", "RTA", "RTD"],
        "FRM": ["PL1", "PL0", "TAG", "DST"],
        "SCP": ["MEM", "TGM", "CDM", "COD"],
        "WCL": ["NOW", "BGN", "END"],
        "WCH": ["NOW", "BGN", "END"],
        "DIO": ["DIR", "INV", "POS", "NEG"],
        "CTR": [None]*N_DIO,
        "FTW": [None]*N_DDS,
        "IOU": [None]*(len(N_COU) if type(N_COU) in (tuple,list) else N_COU),
        "COU": [None]*(len(N_COU) if type(N_COU) in (tuple,list) else N_COU),
        "IIN": [None]*(len(N_CIN) if type(N_CIN) in (tuple,list) else N_CIN),
        "CIN": [None]*(len(N_CIN) if type(N_CIN) in (tuple,list) else N_CIN)} | \
        {f"SPI{n:02X}": ([None]*N_SPI_SEG + ["CTL", "CNT"]) for n in range(N_SPI)},
        8192, 131072)
        for i in range(N_SPI):
            self.__dict__[f'spi{i:02x}'] = spi(i,N_SPI_SEG)
        self.cou = cou(N_COU)
        self.cin = cin(N_CIN)
        self.ftw = ftw(N_DDS)       

    def gpio(self, pos, out=1):
        if type(pos) in (tuple,list):
            return [self.gpio(i,out) for i in pos]
        cfg = self.cou[6+(pos>>5)]
        if out:
            cfg.on(pos&0x1f)
        else:
            cfg.off(pos&0x1f)
        return pin(self.cou if out else self.cin,pos>>5,pos&0x1f)

    def dds(self, chn, f, a, p, o):
        self.ftw[chn](f if isinstance(f, int) else round(f * 2**32 / 250))
        amp(round(a * 0xFFFF))
        pow(round(p * 2**32))
        ofs(round(o * 0x7FFFF))
    
flex = flex(**globals())
flex.config(1,12,6,1)

def shift_out(sclk,mosi,dat,n=8):
    sclk.off()
    for i in range(n):
        mosi((dat>>(n-1-i))&1)
        sclk.on()
        sclk.off()

def shift_in(sclk,miso,reg,n=8):
    R[reg] = 0
    sclk.off()
    for i in range(n):
        sclk.on()
        std.pause(2)
        R[reg] |= miso()<<(n-1-i)
        sclk.off()
        std.pause(2)