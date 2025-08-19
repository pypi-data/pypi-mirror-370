import os,sys,time
PYODIDE = 'pyodide' in sys.modules
if PYODIDE:
    import js,pyodide
try:
    import veri
    veri.lib = os.path.join(os.path.dirname(os.path.realpath(__file__)),sys.platform)
except:
    pass
try:
    import threading
except:
    pass
try:    
    import serial, struct, ctypes
except:
    pass
try:    
    import pcap
except:
    pass
try:    
    import ftd3xx
except:
    pass
from . import bit_concat, bit_split, C_BASE, PL01, pack_frame, unpack_frame, run_cfg

class base_intf:
    EXC_TAG = 0xFFFFF
    LOG_TAG = 0XFFFFE

    def __init__(self):
        self.open_cnt = 0
        self.pad_byt = 0
        self.nod_adr = 0xFFFF
        self.loc_chn = 1
        self.info = dict()
        self.data = dict()
        self.oper = dict()
        self.dev_tot = 0.1
        self.verbose = True
        self.thread = None
    
    def start(self, *args, **kwargs):
        if self.thread and self.thread.running:
            return
        kwargs['target'] = kwargs.get('target',self.run)
        kwargs['name'] = self.__class__.__name__+'-'+kwargs.get('name',str(id(self)))
        kwargs['daemon'] = kwargs.get('daemon',True)
        self.thread = threading.Thread(*args,**kwargs)
        self.thread.start()

    def stop(self):
        if self.thread is not None:
            self.thread.running = False
            self.thread.join()
            self.thread = None

    @classmethod
    def stop_all(cls):
        for thread in threading.enumerate():
            if thread.name.startswith(cls.__name__):
                thread.running = False
                thread.join()

    def run(self):
        import time, queue
        self.thread.running = True
        self.thread.fifo = queue.SimpleQueue()
        if self.open_cnt == 0:
            self.open()
        self.set_timeout(self.dev_tot)
        buf = dict()
        while self.thread.running:
            try:
                self._dev_wr(self.thread.fifo.get(timeout=self.dev_tot))
            except queue.Empty:
                pass            
            frm = self._dev_rd()
            if frm is None:
                continue
            flg,chn,adr,tag,pld = unpack_frame(frm)
            if flg == 4:
                chn,adr,fin = self._proc_info(pld)
            else:
                chn,adr = tag>>16,tag&0xffff
                if adr == 0xffff:
                    adr,fin = self._proc_oper(chn,pld)
                else:
                    fin = self._proc_data(chn,adr,pld)

    def open(self):
        if self.open_cnt == 0:
            self.open_device()
        self.open_cnt += 1
    
    def close(self):
        self.open_cnt -= 1
        if self.open_cnt == 0:
            self.close_device()

    def __enter__(self):
        self.open()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open_device(self):
        raise NotImplementedError()

    def close_device(self):
        raise NotImplementedError()

    def set_timeout(self, tout):
        raise NotImplementedError()

    def _dev_wr(self, dat):
        raise NotImplementedError()

    def _dev_rd(self):
        raise NotImplementedError()

    def _proc_info(self, pld):
        info,chn,adr = bit_split(pld[0],(12,4,16))
        buf = self.info.get((chn<<16)+adr,None)
        if buf is None:
            buf = {}
            self.info[adr] = buf
        buf[info] = pld[1]
        if info == 0:
            print(f"Node #{adr}.{chn}: Exception occurred with flag 0x{buf[0]:08X} at address {buf.get(1,0)}.")
        return chn,adr,info==0

    def _proc_data(self, chn, adr, pld):
        adr += chn<<16
        buf = self.data.get(adr,None)
        if buf is None:
            self.data[adr] = pld
        else:
            buf += pld
        return False
        
    def _proc_oper(self, chn, pld):
        narg,adr = pld[0]>>16,pld[0]&0xffff
        buf = self.data.get((chn<<16)+adr,[])
        fin = False
        if pld[1] == 0:
            if narg == 0:
                if self.verbose:
                    print(f"Node #{adr}.{chn}: Task complete.")
                fin = True
            elif narg == 1:
                if self.verbose:
                    print(f"Node #{adr}.{chn}: Task running.")
        else:
            oper = self.oper.get(pld[1],None)
            if callable(oper):
                oper(buf if narg == 0 else buf[-narg:],run_cfg(self,[adr],chn=chn))
                if narg > 0:
                    self.data[(chn<<16)+adr] = buf[:-narg]
        return adr,fin

    def write(self, flg, chn, adr, tag, pld):
        wcad = C_BASE.RTLK["W_CHN_ADR"]
        wnad = C_BASE.RTLK["W_NOD_ADR"]
        wtag = C_BASE.RTLK["W_TAG_LTN"]
        npld = C_BASE.RTLK["N_FRM_PLD"]
        nhdr = C_BASE.RTLK["N_BYT"] - 4*npld
        hdr = None
        if isinstance(tag, int):
            hdr = bit_concat((flg,3),(chn,wcad),(adr,wnad),(tag,wtag)).to_bytes(nhdr,'big')
            tag = [tag] 
        lpd = len(pld)
        ltg = len(tag)
        if lpd % 2 == 1:
            pld += [0]
            lpd += 1
        dlt = lpd // 2 - ltg
        if dlt > 0:
            tag += [tag[-1]] * dlt
            ltg += dlt
        if hdr is None:
            hdr = [bit_concat((flg,3),(chn,wcad),(adr,wnad),(i,wtag)).to_bytes(nhdr,'big') for i in tag]
        pad = b"\x00" * self.pad_byt
        buf = bytearray()
        for i in range(ltg):
            #buf += pad + pack_frame(flg, chn, adr, tag[i], pld[i*2:i*2+2])
            buf += pad + (hdr[i] if type(hdr) is list else hdr)
            if PL01:
                buf += int(pld[2*i+1]).to_bytes(4,'big')
                buf += int(pld[2*i]).to_bytes(4,'big')
            else:
                buf += int(pld[2*i]).to_bytes(4,'big')
                buf += int(pld[2*i+1]).to_bytes(4,'big')
        self.data = dict()
        if self.thread and self.thread.running:
            self.thread.fifo.put(buf)
        else:
            self._dev_wr(buf)

    def read_raw(self, cnt):
        payloads = []
        for i in range(cnt):
            frm = self._dev_rd()
            if frm is None:
                break
            flg, chn, adr, tag, pld = unpack_frame(frm)
            payloads += pld
        return payloads

    def flush(self):
        self.set_timeout(0.1)
        self.read_raw(3000)

    def monitor(self, nodes, tout):
        mon = set(nodes)
        self.set_timeout(self.dev_tot)
        tot_cnt = 0
        while len(mon):
            frm = self._dev_rd()
            if frm is None:
                tot_cnt += 1
                if tot_cnt == tout:
                    break
                else:
                    continue
            flg,chn,adr,tag,pld = unpack_frame(frm)
            if flg == 4:
                chn,adr,fin = self._proc_info(pld)
            else:
                chn,adr = tag>>16,tag&0xffff
                if adr == 0xffff:
                    adr,fin = self._proc_oper(chn,pld)
                else:
                    fin = self._proc_data(chn,adr,pld)
            if fin:
                mon.remove(adr)
        return self.data
    
class uart_intf(base_intf):
    def __init__(self, port, baud=1000000):
        super().__init__()
        self.port = port
        self.baud = baud
        self.pad_byt = 0

    def open_device(self):
        self.dev = serial.Serial(self.port, self.baud)
        self.dev.stopbits = serial.STOPBITS_TWO
        self.set_timeout(1.0)

    def close_device(self):
        if self.dev is not None:
            self.dev.close()
        self.dev = None

    def set_timeout(self, tout):
        self.dev.timeout = tout
        self.dev.write_timeout = tout

    def _dev_wr(self, dat):
        self.dev.write(dat)
    
    def _dev_rd(self):
        frm = self.dev.read(C_BASE.RTLK["N_BYT"])
        if len(frm) == C_BASE.RTLK["N_BYT"]:
            return frm
        return None

class ft601_intf(base_intf):
    def __init__(self, sn):
        super().__init__()
        self.sn = sn
        self.pad_byt = (4 - C_BASE.RTLK["N_BYT"] % 4) % 4
        self.frm_byt = C_BASE.RTLK["N_BYT"] + self.pad_byt
    
    def open_device(self):
        sn = bytes(self.sn, encoding="utf-8")
        self.dev = ftd3xx.create(sn, ftd3xx.FT_OPEN_BY_SERIAL_NUMBER)
        if self.dev is None:
            raise RuntimeError(f"Incorrect serial number: {self.sn}")
        self.dev.setPipeTimeout(0x02, 1000)
        self.dev.setPipeTimeout(0x82, 1000)

    def close_device(self):
        if self.dev is not None:
            self.dev.close()
        self.dev = None

    def set_timeout(self, tout):
        self.dev_tot = tout

    def _dev_wr(self, dat):
        self.dev.writePipe(0x02, bytes(dat), len(dat))

    def _dev_rd(self):
        byt, frm = self.dev.readPipeEx(0x82, self.frm_byt)
        if byt == self.frm_byt:
            vld = frm[self.pad_byt] >> 4
            if vld == 0:
                return frm
            time.sleep(self.dev_tot)
            return None
        print("USB timeout!")
        self.dev.abortPipe(0x82)
        self.dev.writePipe(0x02, b"\xFF"*self.frm_byt, self.frm_byt)
        return None

class sim_intf(base_intf):
    def __init__(self, top='top', io=['LED'], trace=None):
        super().__init__()
        self.top = top.lower() if type(top) is str else top
        self.io = io
        self.trace = trace
        self.dev_tot = 0.001
        self.pad_byt = 0
        
    def open_device(self):
        if callable(self.top):
            self.dev = self.top()
        else:
            if PYODIDE:
                import json
                js.eval(f'veri.${self.top}=veri.top("rtmq2.{self.top}",{json.dumps(self.io)},self.trace,{C_BASE.RTLK["N_BYT"]})')
                self.dev = getattr(js.veri,f'${self.top}')
                self.dev.run()
            else:
                self.dev = veri.top(self.top,self.io,self.trace,C_BASE.RTLK['N_BYT'])
                self.dev.run()

    def close_device(self):
        if self.dev is not None:
            self.dev.close()
        self.dev = None

    def set_timeout(self, tout):
        self.dev_tot = tout

    def _dev_wr(self, frm):
        self.dev.write(frm)
        
    def _dev_rd(self):
        frm = self.dev.read(C_BASE.RTLK['N_BYT'], self.dev_tot)
        if PYODIDE:
            frm = frm.to_py()
        return frm if len(frm) == C_BASE.RTLK['N_BYT'] else None
    
    def uart(self, port, baud=1000000):
        port = serial.Serial(port,baud)
        try:
            while True:
                if port.in_waiting > 0:
                    self.dev.write(port.read(port.in_waiting))
                else:
                    self.dev.run()
                byt = self.dev.read(1,0)
                if len(byt) > 0:
                    port.write(byt)
        except KeyboardInterrupt:
            port.close()
    
    # def eth(self, eth, dst=None):
    #     eth = eth_intf(eth,dst)
    #     eth.set_timeout(0)
    #     eth.__enter__()
    #     byt = b''
    #     try:
    #         while True:
    #             frm = eth.read()
    #             if len(frm):
    #                 flg, chn, adr, tag, pld = unpack_frame(frm)
    #                 self.dev.write(frm)
    #             else:
    #                 self.dev.run()
    #             byt += self.dev.read(1,0)
    #             if len(byt) == C_BASE.RTLK['N_BYT']:
    #                 eth.write(byt)
    #                 byt = b''
    #     except KeyboardInterrupt:
    #         eth.__exit__(0,0,0)


#! Need revision
"""
class eth_intf(base_intf):
    ETHERTYPE_CUSTOM = 0x88B5
    PADDING_SIZE = 32
    def __init__(self, eth, dst=None):
        import binascii
        if sys.platform == 'linux':
            import fcntl
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                info = fcntl.ioctl(s.fileno(),0x8927, struct.pack('256s',eth[:15].encode()))
                src = info[18:24]
        elif sys.platform.startswith('win'):
            guid,mac = os.popen(f"wmic nic where NetConnectionID='{eth}' get GUID,MACAddress /value").read().strip().split('\n\n')
            eth = r'\\Device\\NPF_' + guid.split('=')[1]
            src = binascii.unhexlify(mac.split('=')[1].replace(':',''))
        self.eth = eth
        self.src = src
        self.dst = binascii.unhexlify(dst.replace(':','')) if dst else src
        self.dev_tot = 5
        super().__init__()

    def open_device(self):
        self.dev = pcap.pcap(name=self.eth,promisc=True,timeout_ms=1)#immediate=True)
        self.dev.setfilter(f'ether proto 0x{self.ETHERTYPE_CUSTOM:04x}')

    def close_device(self):
        if self.dev is not None:
            self.dev.close()
        self.dev = None

    def set_timeout(self, tout):
        self.dev_tot = tout

    def write(self, frm):
        eth_header = self.dst+self.src+struct.pack('!H',self.ETHERTYPE_CUSTOM)
        padding = id(self.dev).to_bytes(8,'big') + b'\x00'*(self.PADDING_SIZE-8)
        n = asm.core.RTLK['N_BYT']
        for i in range(len(frm)//n):
            self.dev.sendpacket(eth_header+padding+frm[i*n:(i+1)*n])
                             
    def read(self):
        dev = self.dev
        pcap._pcap_ex.setup(dev._pcap__pcap)
        hdr  = pcap._pcap._pcap.pkthdr()
        phdr = ctypes.pointer(hdr)
        pkt  = ctypes.POINTER(ctypes.c_ubyte)()
        tout = self.dev_tot
        while True:
            n = pcap._pcap_ex.next_ex(dev._pcap__pcap,ctypes.byref(phdr),ctypes.byref(pkt))    
            if n == -2:
                raise EOFError
            elif n == -1:
                raise KeyboardInterrupt
            elif n == 1:
                hdr = phdr[0]
                ts = hdr.ts.tv_sec+(hdr.ts.tv_usec*dev._pcap__precision_scale)
                buf = ctypes.cast(pkt,ctypes.POINTER(ctypes.c_char*hdr.caplen))[0].raw
            #for ts, pkt in self.dev:
                if int.from_bytes(buf[12:14],'big') != self.ETHERTYPE_CUSTOM or int.from_bytes(buf[14:22],'big') == id(dev):
                    continue
                return buf[14+self.PADDING_SIZE:14+self.PADDING_SIZE+14]
            elif n == 0 and self.dev_tot == 0:
                return b''
            tout -= 0.001
            if tout <= 0:
                raise TimeoutError
"""

# if __name__ == '__main__':
#     intf = sim_intf()
#     with intf:
#         #intf.uart(sys.argv[1])
#         intf.eth(*sys.argv[1:])
