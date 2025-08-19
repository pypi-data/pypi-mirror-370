import math
from contextlib import contextmanager
from .. import *

def bit_concat(*args):
    """

    Bit fields concatenation.

    Parameters
    ----------
    *args : 2-tuples as (V, W)
        Each argument corresponds to a bit field with value V and width W.
        Bit fields are concatenated from high to low.
        NOTE: V will be cropped if not less than (2 ** W)

    Returns
    -------
    dat : integer
        Concatenated value.

    Example
    -------
    bit_concat((0b11, 2), (0b10, 3), (0b11, 1)) == 0b110101

    """
    dat = 0
    ln = len(args)
    for i in range(ln - 1):
        dat |= args[i][0] & ((1 << args[i][1]) - 1)
        dat <<= args[i + 1][1]
    dat |= args[ln - 1][0] & ((1 << args[ln - 1][1]) - 1)
    return dat

def bit_split(dat, wids):
    """

    Split a number into bit fields.

    Parameters
    ----------
    dat : integer
        Number to be splitted.
    wids : list OR tuple of integers
        Width of each bit field.

    Returns
    -------
    bf : list of integers
        Values of bit fields.

    Example
    -------
    bit_split(0b110101, (2, 3, 1)) == [0b11, 0b10, 0b1]

    """
    bf = []
    for i in range(1, len(wids)):
        bf += [dat & ((1<<wids[-i])-1)]
        dat = dat >> wids[-i]
    bf += [dat & ((1<<wids[0])-1)]
    bf.reverse()
    return bf

def to_unsigned(rx, wid=32):
    return rx & ((1 << wid) - 1)

def to_signed(rx, wid=32):
    return -(rx & (1 << (wid - 1))) | (rx & ((1 << wid) - 1))

class base_core:
    RSV = ["PTR", "LNK", "RSM", "EXC", "EHN", "STK"]
    RTLK = {"W_CHN_ADR": 5,
            "W_NOD_ADR": 16,
            "W_TAG_LTN": 20,
            "N_FRM_PLD": 2,
            "W_FRM_PAD": 4}
    OPC = {"NOP": [ 0, "-HP", "" , ""  , ""    ],
           "SFS": [ 0, "-"  , "C", "CG" , ""    ],
           "CHI": [ 8, "-"  , "C", "I" , ""    ],
           "CLO": [ 9, "-HP", "C", "I" , ""    ],
           "AMK": [13, "-HP", "C", "NG", "NICG"],
           "AND": [ 0, "-"  , "G", "IG", "IG"  ],
           "IAN": [ 1, "-"  , "G", "IG", "IG"  ],
           "BOR": [ 2, "-"  , "G", "IG", "IG"  ],
           "XOR": [ 3, "-"  , "G", "IG", "IG"  ],
           "CSR": [ 4, "-"  , "G", "C" , ""    ],
           "GHI": [ 5, "-"  , "G", "I" , ""    ],
           "SGN": [ 6, "-"  , "G", "IG", "IG"  ],
           "OPL": [ 7, "-"  , "G", "IG", ""    ],
           "PLO": [ 0, "-"  , "G", ""  , ""    ],
           "PHI": [ 1, "-"  , "G", ""  , ""    ],
           "DIV": [ 2, "-"  , "G", ""  , ""    ],
           "MOD": [ 3, "-"  , "G", ""  , ""    ],
           "GLO": [ 8, "-"  , "G", "I" , ""    ],
           "ADD": [12, "-"  , "G", "IG", "IG"  ],
           "SUB": [13, "-"  , "G", "IG", "IG"  ],
           "CAD": [14, "-"  , "G", "IG", "IG"  ],
           "CSB": [15, "-"  , "G", "IG", "IG"  ],
           "NEQ": [16, "-"  , "G", "IG", "IG"  ],
           "EQU": [17, "-"  , "G", "IG", "IG"  ],
           "LST": [18, "-"  , "G", "IG", "IG"  ],
           "LSE": [19, "-"  , "G", "IG", "IG"  ],
           "SHL": [20, "-"  , "G", "IG", "IG"  ],
           "SHR": [21, "-"  , "G", "IG", "IG"  ],
           "ROL": [22, "-"  , "G", "IG", "IG"  ],
           "SAR": [23, "-"  , "G", "IG", "IG"  ]}

    def __init__(self, csr, nums, sbfs, cap_ich, cap_dch):
        self.CSR = self.RSV + csr
        self.csr = dict()
        for i in range(len(self.CSR)):
            if self.CSR[i] is not None:
                self.csr[self.CSR[i]] = i
        self.NUM = ["PTR", "STK"] + nums
        self.SBF = sbfs
        self.sbfs = dict()
        for k, v in self.SBF.items():
            self.sbfs[k] = dict()
            for i in range(len(v)):
                if v[i] is not None:
                    self.sbfs[k][v[i]] = i
        self.CAP_ICH = cap_ich
        self.CAP_DCH = cap_dch
        wcad = self.RTLK["W_CHN_ADR"]
        wnad = self.RTLK["W_NOD_ADR"]
        wtag = self.RTLK["W_TAG_LTN"]
        npld = self.RTLK["N_FRM_PLD"]
        wpad = self.RTLK["W_FRM_PAD"]
        flen = 3 + wcad + wnad + wtag + npld * 32 + wpad
        self.RTLK["N_BYT"] = flen // 8

PL01 = False

C_BASE = base_core([], [], {}, 65536, 16384)
C_STD = base_core(
    ["ICF", "ICA", "ICD", "DCF", "DCA", "DCD",
     "NEX", "FRM", "SCP", "TIM", "WCL", "WCH", "LED", "TRM"],
    ["ICA", "DCA"],
    {"NEX": [None]*32 + ["ADR", "BCE", "RTA", "RTD"],
     "FRM": (["PL0", "PL1"] if PL01 else ["PL1", "PL0"])+["TAG", "DST"],
     "SCP": ["MEM", "TGM", "CDM", "COD"],
     "WCL": ["NOW", "BGN", "END"],
     "WCH": ["NOW", "BGN", "END"]},
    65536, 16384)

asm = context(core=C_STD)
        
class disassembler:
    OPC_TYA = ["AND", "IAN", "BOR", "XOR", "CSR", "GHI", "SGN", "", "", "", "", "", 
               "ADD", "SUB", "CAD", "CSB", "NEQ", "EQU", "LST", "LSE", "SHL", "SHR", "ROL", "SAR"]
    OPC_EXT = ["PLO", "PHI", "DIV", "MOD"]

    def __init__(self, core=None):
        self.core = core
        self.stat = 0

    def _csr(self, adr):
        try:
            ret = self.core.CSR[adr] or f"&{csr:02X}"
        except:
            ret = f"&{adr:02X}"
        return ret

    def _sbf(self, adr, csr):
        try:
            ret = self.core.SBF[self.core.CSR[adr]][csr] or f"&{csr:02X}" 
        except:
            ret = f"&{csr:02X}"
        return ret

    def _imm(self, imm, typ):
        if typ == 0:
            return str(to_signed(imm, 8))
        if typ == 1:
            return f"{imm>>4:01X}.{imm%16:01X}"
        if typ == 2:
            return f"0x000_{imm:05X}"
        if typ == 3:
            return f"0x{imm:03X}_00000"
        if typ == 4:
            return str(to_signed(imm, 20))
        return ""

    def _cli(self, ard, trd, tia, fhp, trs, tr0, tr1, ar0, ar1):
        rd = self._csr(ard)
        if fhp == 0:
            if trs == 0:
                return f"CHI - {rd} {self._imm(bit_concat((ar0, 4), (ar1, 8)), 3)}"
            else:
                r1 = f"${ar1:02X}" if tr1 else self._sbf(ard, ar1)
                return f"SFS - {rd} {r1}"
        else:
            tmp = bit_concat((trs, 2), (tr0, 1), (tr1, 1), (ar0, 8), (ar1, 8))
            return f"CLO {'-HP'[fhp-1]} {rd} {self._imm(tmp, 2)}"
    
    def _amk(self, ard, trd, tia, fhp, trs, tr0, tr1, ar0, ar1):
        rd = self._csr(ard)
        hp = '-HP'[fhp-1]
        if (ard, trs, tr0, tr1, ar0, ar1) == (0, 0, 0, 0, 0, 0):
            return f"NOP {hp}"
        r0 = f"${ar0:02X}" if tr0 else self._imm(ar0, 1)
        r1 = self._imm(ar1, 1-tr1) if trs % 2 == 0 else (f"${ar1:02X}" if tr1 else self._csr(ar1))
        return f"AMK {hp} {rd} {r0} {r1}"
    
    def _alu(self, ard, trd, tia, fhp, trs, tr0, tr1, ar0, ar1):
        rd = f"${ard:02X}"
        r0 = f"${ar0:02X}" if tr0 else self._imm(ar0, 0)
        r1 = f"${ar1:02X}" if tr1 else self._imm(ar1, 0)
        opc = bit_concat((tia, 1), (fhp, 2), (trs, 2))
        if opc >> 2 == 2:
            tmp = bit_concat((trs, 2), (tr0, 1), (tr1, 1), (ar0, 8), (ar1, 8))
            return f"GLO - {rd} {self._imm(tmp, 4)}"
        fop = self.OPC_TYA[opc]
        if opc in (4, 5):
            r1 = self._csr(ar1) if opc == 4 else self._imm(bit_concat((ar0, 4), (ar1, 8)), 3)
            return f"{fop} - {rd} {r1}"
        if opc == 7:
            if (tr0, tr1) == (0, 0):
                return f"{self.OPC_EXT[ar1 % 4]} - {rd}"
            else:
                return f"OPL - {r0} {r1}"
        return f"{fop} - {rd} {r0} {r1}"

    def _disa(self, code, idx_str=None, idx_wid=1):
        prg = []
        for i in range(len(code)):
            fld = bit_split(code[i], (8, 1, 1, 2, 2, 1, 1, 8, 8))
            ins = (self._amk(*fld) if fld[2] else self._cli(*fld)) if fld[1] else self._alu(*fld)
            idx = "" if idx_str is None else f"{idx_str+i:0{idx_wid}X}: "
            prg += [idx + ins]
        if idx_str is None:
            return prg
        else:
            return "\n".join(prg)

    def __call__(self, *args, **kwargs):
        if self.stat == 0:
            self.func = args[0]
            self.idxs = args[1] if len(args) >= 2 else None
            self.idxw = args[2] if len(args) >= 3 else 4
            if self.core is None:
                self.core = getattr(self.func,'core',asm.core)
            if type(self.func) in (tuple,list,table):
                return self._disa(self.func[:], self.idxs, self.idxw)
            self.stat = 1
            return self
        self.stat = 0
        with asm:
            asm.core = self.core
            self.func(*args, **kwargs)
            return self._disa(asm[:], self.idxs, self.idxw)
        
def label(tag,put=True):
    lbl = getattr(asm,'label',None)
    if lbl is None:
        lbl = {}
        asm.label = lbl
    if type(tag) is str:
        tag = tag.upper()
    pos = lbl.get(tag,None)
    if put is True or type(put) in (int,list):
        if put is True:
            put = len(asm)
        if type(put) is int:
            if type(pos) is list:
                if type(pos[0]) is expr and len(pos[0]) == 1 and type(pos[0][:][0]) is not expr:
                    pos[0][0] = put
                for i in pos[1:]:
                    if type(asm[i]) is not int:
                        asm[i] = asm[i]()
        lbl[tag] = put
    else:
        if type(pos) is int:
            return pos
        if pos is None:
            if not isinstance(put,expr):
                put = expr(put)
            pos = [put]
            lbl[tag] = pos
        pos.append(len(asm))
        return pos[0]
 
def cnv_opd(opd, idx, opc):
    if type(opd) is expr:
        return (label(id(opd),opd),1)
    try:
        field = ["flag", "RD", "R0", "R1"][idx-1]
        typ = asm.core.OPC[opc][idx]
        if type(opd) is int:
            if "I" not in typ:
                raise
            return (opd & 0xFFFF_FFFF, 1)
        opd = str(opd).upper()
        if idx == 1:
            res = typ.find(opd)
            return 0 if res < 0 else res
        if opd in asm.core.CSR:
            if "C" not in typ:
                raise
            res = (asm.core.csr[opd], 2)
        elif "." in opd:
            nib, pos = opd.split(".")
            nib = int(nib, 16)
            pos = int(pos, 16)
            if not ((0 <= nib < 16) and (0 <= pos < 16) and ("N" in typ)):
                raise
            res = ((nib << 4) + pos, 0)
        elif opd[0] == "&":
            reg = int(opd[1:], 16)
            if ("C" not in typ) or (reg > 255):
                raise
            res = (reg, 2)
        elif opd[0] == "$":
            reg = int(opd[1:], 16)
            if ("G" not in typ) or (reg > 255):
                raise
            res = (reg, 3)
        elif opd[0] == '#':
            if "I" not in typ:
                raise
            res = (label(opd[1:],None), 1)
        else:
            res = (int(opd,0) & 0xFFFF_FFFF, 1)
            if "I" not in typ:
                raise
    except:
        raise SyntaxError(f"Invalid {field} for {opc}: '{opd}'.")
    return res

H = 1
P = 2

def bubble(r, *args):
    bubl = getattr(asm,'bubble',None)
    if bubl is False:
        return
    for i in args:
        if type(i) is not int and str(i) == bubl:
            nop()
            break
    asm.bubble = None if r is None else str(r) 

def nop(n=1,hp=0):
    bubble(None)
    if n < 0:
        ins = (13-n)<<20
        asm(ins)
    else:
        ins = [(13+hp)<<20]*n
        asm.extend(ins)
    return ins

def sfs(sbf,csr):
    bubble(None,csr)
    sbf = sbf.upper()
    RD, trd = cnv_opd(sbf,2,'SFS')
    if sbf[0] != "&" and sbf not in asm.core.SBF.keys():
        raise SyntaxError(f"'{sbf}' is not a register subfile.")
    csr = f'&{csr:02X}' if type(csr) is int else str(csr).upper()
    if csr[0] in '&$':
        R0, tr0 = cnv_opd(csr,3,'SFS')
        tr0 = tr0 % 2
    elif csr in asm.core.SBF[sbf]:
        R0 = asm.core.sbfs[sbf][csr]
        tr0 = 0
    else:
        raise SyntaxError(f"Invalid register '{csr}' in sub-file {sbf}.")
    ins = bit_concat((RD, 8), (8, 4), (8 + tr0, 4), (R0, 16))
    asm(ins)
    return ins

def opc0(opc,rd):
    return asm.core.OPC[opc][0],*cnv_opd(rd,2,opc)

def opr(opc,rd):
    bubble(rd)
    opcd,RD,trd = opc0(opc,rd)
    ins = bit_concat((RD, 8), (7, 6), (0, 2), (0, 8), (opcd, 8))
    asm(ins)
    return ins
    
for k in ('PLO','PHI','DIV','MOD'):
    globals()[k.lower()] = (lambda k:lambda rd:opr(k,rd))(k)
    
def opc1(opc,rd,r0):
    return *opc0(opc,rd),*cnv_opd(r0,3,opc)

def ghi(rd,r0):
    bubble(rd)
    opcd,RD,trd,R0,tr0 = opc1('GHI',rd,r0)
    ins = bit_concat((RD, 8), (opcd, 6), (0, 2), (R0 >> 20, 16))
    asm(ins)
    return ins

def glo(rd,r0):
    bubble(rd)
    opcd,RD,trd,R0,tr0 = opc1('GLO',rd,r0)
    ins = bit_concat((RD, 8), (2, 4), (R0, 20))
    asm(ins)
    return ins

def gli(rd,r0):
    return glo(rd,r0) if r0 == to_signed(r0,20) else [glo(rd,r0),ghi(rd,r0)]

def csr(rd,r0):
    bubble(rd)
    opcd,RD,trd,R0,tr0 = opc1('CSR',rd,r0)
    ins = bit_concat((RD, 8), (opcd, 6), (0, 2), (0, 8), (R0, 8))
    asm(ins)
    return ins
        
def chi(rd,r0):
    bubble(None)
    opcd,RD,trd,R0,tr0 = opc1('CHI',rd,r0)
    ins = bit_concat((RD, 8), (opcd, 4), (R0 >> 20, 20))
    asm(ins)
    return ins
    
def clo(rd,r0,hp=0):
    bubble(None)
    opcd,RD,trd,R0,tr0 = opc1('CLO',rd,r0)
    ins = bit_concat((RD, 8), (opcd + hp, 4), (R0, 20))
    asm(ins)
    return ins

def cli(rd,r0,hp=0):
    return [chi(rd,r0),clo(rd,r0,hp)]

def opl(rd,r0):
    bubble(None,rd,r0)
    opcd,RD,trd,R0,tr0 = opc1('OPL',rd,r0)
    ins = bit_concat((0, 8), (7, 6), (trd, 1), (tr0 >> 1, 1), (RD, 8), (R0, 8))
    asm(ins)
    return ins
    
def opc2(opc,rd,r0,r1):
    return *opc1(opc,rd,r0),*cnv_opd(r1,4,opc)

def amk(rd,r0,r1,hp=0):
    bubble(None,r0,r1)
    opcd,RD,trd,R0,tr0,R1,tr1 = opc2('AMK',rd,r0,r1)
    ins = bit_concat((RD, 8), (opcd + hp, 4), (tr1 >> 1, 2), (tr0, 1), (tr1, 1), (R0, 8), (R1, 8))
    asm(ins)
    return ins

def alu(opc,rd,r0,r1):
    bubble(rd,r0,r1)
    opcd,RD,trd,R0,tr0,R1,tr1 = opc2(opc,rd,r0,r1)
    ins = bit_concat((RD, 8), (opcd, 6), (tr0 >> 1, 1), (tr1 >> 1, 1), (R0, 8), (R1, 8))
    asm(ins)
    return ins

for k in base_core.OPC.keys()-('NOP','SFS','CHI','CLO','AMK','CSR','GHI','OPL','PLO','PHI','DIV','MOD','GLO'):
    globals()['and_' if k == 'AND' else k.lower()] = (lambda k:lambda rd,r0,r1:alu(k,rd,r0,r1))(k)

def mul(r, a, b):
    opl(a, b)
    nop(1, P)
    plo(r)

def div_u(r, a, b):
    opl(a, b)
    nop(5, P)
    nop()
    div(r)

def rem_u(r, a, b):
    opl(a, b)
    nop(5, P)
    nop()
    mod(r)

def mov(rd,r0,hp=0):
    if rd is None or r0 is None:
        return
    if type(r0) is int:
        if r0 == 0:
            return mov(rd,'$00',hp)
        elif r0&0xffffffff == 0xffffffff:
            return mov(rd,'$01',hp)
    rd = str(rd)
    if callable(r0) and type(r0) is not expr:
        if rd[0] != '$' and str(r0)[0] == '<':
            r0(tmp(-1))
            return mov(rd,tmp(-1),hp)
        else:
            return r0(rd)
    if rd[0] == '$':
        if type(r0) in (int,expr):
            return gli(rd,r0)
        r0 = str(r0)
        if r0[0] == '$':
            if rd == r0:
                return
            else:
                return add(rd,'$00',r0)
        else:
            if '.' in r0:
                r0,sub = r0.split('.')
                sfs(r0, sub)
                nop(1,P)
            return csr(rd, r0)          
    else:
        if '.' in rd:
            rd, sub = rd.split('.')
            sfs(rd, sub)
        if type(r0) in (int,expr):
            return cli(rd,r0,hp)
        elif type(r0) in (tuple,list): 
            r0,msk = r0
            top = tmp.top            
            if type(r0) in (int,expr):
                if type(msk) is int:
                    if msk == 0xfffff:
                        return clo(rd,r0,hp)
                    elif msk == 0xfff00000:
                        return chi(rd,r0)
                r0 = tmp(None,r0)
            elif callable(r0) and type(r0) is not expr:
                r0 = tmp(None,r0)
            if type(msk) is int:
                sca = int(math.log2(msk & -msk))
                if sca & 1:
                    sca -= 1
                msk >>= sca
                if msk < 0x10 and sca < 0x20:
                    msk = f'{msk:x}.{(sca>>1):x}'
                else:
                    msk = tmp(None,msk<<sca,False)
            elif callable(msk) and type(msk) is not expr:
                msk = tmp(None,msk)
            tmp.top = top
            return amk(rd,msk,r0,hp)
        r0 = str(r0)
        if '.' in r0:
            r0,sub = r0.split('.')
            sfs(r0, sub)
            nop(1,P)
        msk = '2.0' if rd.upper() in asm.core.NUM else '$01'
        return amk(rd,msk,r0,hp)

def tmp(rd,r0=None,imm=True):
    if type(rd) is int:
        rd = f'${((tmp.base if rd >= 0 else tmp.top)+rd):02X}'
    if r0 is None:
        return rd
    if type(r0) is int:
        if r0 == 0:
            return '$00'
        elif r0&0xffffffff == 0xffffffff:
            return '$01'
    if not (imm and type(r0) is int and r0 == to_signed(r0,8) or str(r0)[0] == '$'):
        if rd is None:
            tmp.top -= 1
            rd = f'${tmp.top:02X}'
        mov(rd, r0)
        r0 = rd
    return r0

tmp.base = 0xf0
tmp.top = 0x100

@multi(asm)
def inline(prg):
    if type(prg) not in (tuple,list):
        prg = str(prg).splitlines()
    for line in prg:
        instr = line.strip()
        if len(instr) == 0 or instr[0] == '%':
            continue
        if instr[0] == '#' and instr[-1] == ':':
            label(instr[1:-1])
        else:
            instr = instr.split()
            if len(instr) == 1:
                asm(int(instr[0],16))
            else:
                opc = instr[0].lower()
                hp = instr[1]
                if hp == '-':
                    globals()['and_' if opc == 'and' else opc](*instr[2:])
                else:
                    globals()[opc](*instr[2:],hp=cnv_opd(hp,1,opc.upper()))
                    
# -----------------------------------------------------------------------------
# --------- StdLib ------------------------------------------------------------
# -----------------------------------------------------------------------------

def init01():
    glo('$00',0)
    glo('$01',-1)
    nop()

@multi(asm)
def setup(core=C_STD,dnld=1):
    asm.core = core
    asm.dnld = dnld

@multi(asm)
def finish():
    dnld = getattr(asm,'dnld',1)
    if dnld:
        intf_send(oper=0)
        nop(2, H)
        pos = len(asm[:])
        intf_send('lnk', info=1)
        intf_send('exc', info=0)
        nop(2, H)
    flw = asm()
    with asm as cfg:
        if dnld:
            clo("exc", 1, P)
            chi("exc", 0)
            chi("rsm", 0)
            clo("rsm", 1)
            glo("$00", 0)
            glo("$01", -1)
            ich_dnld(flw[:], 0)
            amk("exc", "0.0", "exc")
            amk("ptr", "2.0", 0, P)
            cli("ehn", pos)
            amk("stk", "2.0", 0)
            amk("exc", "1.0", "0.0", P)
        else:
            set_bit("exc", "1.0", P)
            asm.extend(flw[:])
            clr_bit("exc", "1.0", P)
    flw.clear()
    flw.extend(cfg[:])

def w2h(w):
    if type(w) not in (tuple,list):
        w = [w]
    h = []
    for i in w:
        h += [i&0xFFFF,i>>16]
    return h

@multi(asm)
def copy(dst, src, align=4, batch=None):
    if batch is None:
        batch = getattr(asm,'dnld',1)
    if type(dst) not in (tuple,list) and type(src) not in (tuple,list):
        return mov(dst,src)
    if type(dst) not in (tuple,list):
        if len(src) == 1:
            mov('dcf', (align&3)<<30)
            mov('dca', dst)
            mov('dcd', src[0])
        else:
            mov('dcf', ((align&3)<<30)+(len(src) if batch else 0))
            if batch:
                mov('dca', dst)
                for s in src:
                    if type(s) is int:
                        clo('dcd', s)
                    else:
                        mov('dcd', s)
            else:
                mov(tmp(0), dst)
                for i in range(len(src)):
                    mov('dca', tmp(0))
                    add(tmp(0), tmp(0), align)
                    mov('dcd', src[i])
    elif type(src) not in (tuple,list):
        if len(dst) == 1:
            mov('dcf', (align&3)<<30)
            mov('dca', src)
            nop(1, P)
            nop(2)
            mov(dst[0], 'dcd')
        else:
            mov('dcf', ((align&3)<<30)+(len(dst) if batch else 0))
            if batch:
                mov('dca', src)
                nop(1, P)
                nop(2)
                for d in dst:
                    if type(d) is int:
                        asm(d)
                    else:
                        mov(d, 'dcd')
            else:
                mov(tmp(0), src)
                for i in range(len(dst)):
                    mov('dca', tmp(0))
                    add(tmp(0), tmp(0), align)
                    nop(1, P)
                    nop(1)
                    mov(dst[i], 'dcd')
    else:
        for i in range(min(len(dst),len(src))):
            mov(dst[i], src[i])
                
def block(*args):
    blk = [None] if len(args) == 0 else list(args)
    if blk[0] is None:
        pos = expr(0)
        label(id(pos),[pos])
        blk[0] = pos
    if type(blk[-1]) is dict:
        lbl = blk.pop()
        for k,v in lbl.items():
            asm[k] = v
        label(id(blk[0]),[blk[0]]+list(lbl.keys()))
    asm.block = [blk] + getattr(asm,'block',[])

def loop(*args):
    block(len(asm),*args)

@multi(asm)
def end(tag=None):
    if len(getattr(asm,'block',[])) == 0:
        return
    blk = asm.block[0]
    if len(blk) > 1:
        if blk[1] == 'while':
            br(0)
        elif blk[1] == 'for':
            rd,step = blk[2:]
            add(rd, rd, tmp(-1,step))
            br(0)
    pos = blk[0]
    if type(pos) is expr:
        lbl = asm.label[id(pos)]
        blk.append({k:asm[k] for k in lbl[1:]})
        label(id(pos))
        del asm.label[id(pos)]
    asm.block = asm.block[1:]
    if len(blk) > 1 and tag != blk[1]:
        if type(blk[1]) is str and blk[1] in ('if','elif','while','for'):
            end()
    return blk

def br(depth=0):
    pos = asm.block[depth][0]
    rel = pos-len(asm)-2
    if type(pos) is expr:
        label(id(pos),None)
    glo(tmp(-1), rel)
    if type(pos) is expr:
        del asm.label[id(rel)]
    amk('ptr', '3.0', tmp(-1), P)

def br_if(a, depth=0, met=None):
    pos = asm.block[depth][0]
    rel = pos-len(asm)-(2 if met is None else 3)
    if type(pos) is expr:
        label(id(pos),None)
    glo(tmp(-1), rel)
    if type(pos) is expr:
        del asm.label[id(rel)]
    if met is None:
        amk('ptr', a, tmp(-1), P)
    else:
        (neq if met else equ)(tmp(-2), a, '$00')
        amk('ptr', tmp(-2), tmp(-1), P)
        
@multi(asm)
def if_(cond):
    block()
    block(None,'if')
    br_if(tmp(-2,cond), 0, False)

@multi(asm)
def else_():
    br(1)
    end('if')

@multi(asm)
def elif_(cond):
    else_()
    block(None,'elif')
    block(None,'if')
    br_if(tmp(-2,cond), 0, False)

@multi(asm)    
def while_(cond=None):
    block()
    loop('while')
    if cond is not None:
        br_if(tmp(-2,cond), 1, False)

@multi(asm)
def for_(rd,rng):
    if type(rng) not in (tuple,list):
        rng = (rng,)
    if len(rng) == 1:
        start = 0
        stop = rng[0]
    else:
        start = rng[0]
        stop = rng[1]
    step = rng[2] if len(rng) > 2 else 1
    block()
    mov(rd, start)
    loop('for', rd, step)
    lse(tmp(-2), tmp(-1,stop), rd)
    br_if(tmp(-2), 1)

@contextmanager
def If(cond):
    try:
        yield if_(cond)
    except Exception:
        raise
    else:
        asm.last_if = [end('if'),end()]

@contextmanager
def Elif(cond):
    try:
        for i in range(min(3,len(asm.last_if))):
            block(*asm.last_if.pop())
        yield elif_(cond)
    except Exception:
        raise
    else:
        asm.last_if += [end('if'),end('elif'),end()]

@contextmanager
def Else():
    try:
        while len(asm.last_if):
            block(*asm.last_if.pop())
        yield else_()
    except Exception:
        raise
    else:
        end()

@contextmanager
def While(cond=None):
    try:
        yield while_(cond)
    except Exception:
        raise
    else:
        end()

@contextmanager
def For(rd, rng):
    try:
        yield for_(rd,rng)
    except Exception:
        raise
    else:
        end()

def frame(*args):
    if len(args) == 0:
        return getattr(asm, 'frame', (0,))
    asm.frame = args
    vars = [R[i] for i in range(2+sum(args))]
    vars = vars[:args[0]]+vars[(args[0]+2):]
    return vars[0] if len(vars) == 1 else vars

def function(name, args=0, locals=0):
    bubble(None)
    label(name)
    sub(f'${(0x20+args):02X}', '$00', f'${(0x20+args):02X}')
    csr(f'${(0x21+args):02X}', 'lnk')
    return frame(args,locals)

def return_(*rets):
    args = frame()[0]
    stk = f'${(0x20+args):02X}'
    lnk = f'${(0x21+args):02X}'
    if len(rets) > args:
        mov(tmp(-1), stk)
        stk = tmp(-1)
        if len(rets) > args + 1:
            mov(tmp(-2), lnk)
            lnk = tmp(-2)
    for i in range(len(rets)):
        mov(f'${(0x20+i):02X}', rets[i])
    amk('stk', '3.0', stk)
    amk('ptr', '2.0', lnk, P)

def call(func, *args):
    size = 2+sum(frame())  
    mov(f'${(0x20+size+len(args)):02X}', size)
    for i in range(len(args)):
        mov(f'${(0x20+size+i):02X}', args[i])
    if type(func) is str and func[0] != '#':
        func = '#' + func
    if size > 0:
        amk('stk', '3.0', f'${(0x20+size+len(args)):02X}')
    clo('ptr', func, P)
    return R[size]

Return = return_
Call = call

@contextmanager
def Func(name, *regs):
    try:
        if len(regs) == 1:
            args = regs[0] + 1
            locals = 0
        else:
            args = regs[0] - 2
            locals = regs[1] + 1 - regs[0]
        yield function(name,args,locals)
    except Exception:
        raise
    else:
        lnk = f'${(0x21+frame()[0]):02X}'
        core = asm.core
        with asm:
            asm.core = core
            ins = amk('ptr', '2.0', lnk, P)
        if asm[-1] != ins:
            return_()
            
Set = mov

class core_reg:
    def __init__(self, key=None, base=0x20):
        if type(key) is int:
            key = f'${(key+base):02X}'
        elif type(key) is str:
            key = key.upper()
        elif type(key) is self.__class__:
            key = key._key
        object.__setattr__(self,'_key',key)
        object.__setattr__(self,'_base',base)
    def __repr__(self):
        return str(self._key)
    def __getattr__(self, key):
        return self[key]
    def __getitem__(self, key):
        if self._key is None:
            if type(key) is slice:
                return [self[i] for i in range(256)[key]]
            key = f'${(key+self._base):02X}' if type(key) is int else str(key).upper()
            val = self.__dict__.get(key, None)
            if val is None:
                val = self.__class__(key)
                self.__dict__[key] = val
            return val
        elif type(self._key) is str and self._key[0] != '$':
            sfs(self._key, key)
            nop(1, P)
            return self
    def __setattr__(self, key, val):
        self[key] = val
    def __setitem__(self, key, val):
        if self._key is None:
            key = f'${(key+self._base):02X}' if type(key) is int else str(key).upper()
            Set(key, val._key if type(val) is self.__class__ else val)
        elif type(self._key) is str and self._key[0] != '$':
            key = self._key + '.' + (f'&{key:02X}' if type(key) is int else str(key).upper())
            Set(key, val._key if type(val) is self.__class__ else val)
    def __dir__(self):
        if self._key is None:
            return asm.core.CSR
        elif type(self._key) is str and self._key[0] != '$':
            return asm.core.SBF[self._key]
    def __call__(self, rd):
        Set(rd, self._key)
    def _oper(self, oper, other):
        def wrap(rd):
            top = tmp.top
            r0 = tmp(rd if str(rd) == f'${tmp.top:02X}' else None,self,oper not in (mul,div_u,rem_u))
            r1 = tmp(rd if str(rd) == f'${tmp.top:02X}' and r0 != rd else None,other)
            oper(rd,r0,r1)
            tmp.top = top
        return self.__class__(wrap)
    def _roper(self, oper, other):
        def wrap(rd):
            top = tmp.top
            r0 = tmp(rd if str(rd) == f'${tmp.top:02X}' else None,other,oper not in (mul,div_u,rem_u))
            r1 = tmp(rd if str(rd) == f'${tmp.top:02X}' and r0 != rd else None,self)
            oper(rd,r0,r1)
            tmp.top = top
        return self.__class__(wrap)
    def __eq__(self, other):
        return self._oper(equ, other)
    def __ne__(self, other):
        return self._oper(neq, other)
    def __lt__(self, other):
        return self._oper(lst, other)
    def __gt__(self, other):
        return self._roper(lst, other)
    def __le__(self, other):
        return self._oper(lse, other)
    def __ge__(self, other):
        return self._roper(lse, other)
    def __add__(self, other):
        return self._oper(add, other)
    def __sub__(self, other):
        return self._oper(sub, other)
    def __mul__(self, other):
        return self._oper(mul, other)
    def __truediv__(self, other):
        return self._oper(div_u, other)
    def __mod__(self, other):
        return self._oper(rem_u, other)
    def __and__(self, other):
        return self._oper(and_, other)
    def __or__(self, other):
        return self._oper(bor, other)
    def __xor__(self, other):
        return self._oper(xor, other)
    def __lshift__(self, other):
        return self._oper(shl, other)
    def __rshift__(self, other):
        return self._oper(sar, other)
    def __radd__(self, other):
        return self._roper(add, other)
    def __rsub__(self, other):
        return self._roper(sub, other)
    def __rmul__(self, other):
        return self._roper(mul, other)
    def __rtruediv__(self, other):
        return self._roper(div_u, other)
    def __rmod__(self, other):
        return self._roper(rem_u, other)
    def __rand__(self, other):
        return self._roper(and_, other)
    def __ror__(self, other):
        return self._roper(bor, other)
    def __rxor__(self, other):
        return self._roper(xor, other)
    def __rlshift__(self, other):
        return self._roper(shl, other)
    def __rrshift__(self, other):
        return self._roper(sar, other)
    def __neg__(self):
        return 0 - self
    def __invert__(self):
        return self._oper(ian, '$01')
    def __imatmul__(self, other):
        R[self] = other
        return self
    def __iadd__(self, other):
        R[self] = self + other
        return self
    def __isub__(self, other):
        R[self] = self - other
        return self
    def __imul__(self, other):
        R[self] = self * other
        return self
    def __itruediv__(self, other):
        R[self] = self / other
        return self
    def __imod__(self, other):
        R[self] = self % other
        return self
    def __iand__(self, other):
        R[self] = self & other
        return self
    def __ior__(self, other):
        R[self] = self | other
        return self
    def __ixor__(self, other):
        R[self] = self ^ other
        return self
    def __ilshift__(self, other):
        R[self] = self << other
        return self
    def __irshift__(self, other):
        R[self] = self >> other
        return self
    
R = core_reg()
        
core_ctx = lambda core=asm.core:{k:R[k] for k in core.CSR}|{k:globals()[k] for k in ('Set','If','Elif','Else','While','For','Return','Call','Func')}
core_regq = lambda core=asm.core:lambda s:s == 'R' or s in core.CSR
core_domain = lambda core=asm.core,sub=True,dump=False:domain(core_ctx(core),core_regq(core),sub=sub,dump=dump)

class core_cache:
    def __init__(self, typ, ptr=0, align=4):
        self.typ = typ
        self.ptr = ptr
        self.align = align
    def __setitem__(self, key, val):
        if type(val) not in (tuple,list):
            val = [val]
        if self.typ[0] == 'd':
            sca = 2 if self.align > 2 else (self.align-1)
            copy((key if sca==0 else (key<<sca))+self.ptr,val,self.align,False)
        else:
            for i in range(len(val)):
                mov('ica', key+i)
                mov('icd', val[i])
    def __getitem__(self, key):
        if self.typ[0] == 'd':
            sca = 2 if self.align > 2 else (self.align-1)
            copy([None],(key if sca==0 else (key<<sca))+self.ptr,self.align,False)
            return R.dcd
        else:
            mov('ica', key)
            nop(1,P)
            return R.icd
    def __add__(self, ptr):
        return self.__class__(self.typ,self.ptr+ptr,self.align)
    def __call__(self, size, align=None):
        ptr = getattr(asm,self.typ,0)
        asm[self.typ] = ptr+size*(align or self.align)
        return self.__class__(self.typ,self.ptr+ptr,align or self.align)

DCH = core_cache('dat')
ICH = core_cache('ins')

def set_csr(csr, val, msk=None, hp=0, align=False):
    gap = True
    if "." in csr:
        csr, sub = csr.split(".")
        gap = False
        sfs(csr, sub)
    if isinstance(val, str) and val[0] != "#":
        if gap and align:
            nop()
        if msk is None:
            msk = "2.0" if csr.upper() in asm.core.NUM else "$01"
        amk(csr, msk, val, hp)
    else:
        cli(csr, val, hp)

def set_bit(csr, msk, hp=0):
    set_csr(csr, "$01", msk, hp)

def clr_bit(csr, msk, hp=0):
    set_csr(csr, "$00", msk, hp)

@multi(asm)
def count_down(dur, strict=True):
    if isinstance(dur, int):
        dur = dur - 1
    set_csr("tim", dur, "2.0")
    if strict:
        set_bit("exc", "2.0")
    else:
        clr_bit("exc", "2.0")
    set_bit("rsm", "4.0")

@multi(asm)
def wait(dur=None):
    if dur is not None:
        count_down(dur, False)
    nop(1, H)

def get_wck(lo, hi):
    mov(lo, "wcl")
    mov(hi, "wch")

def jmp_rel(dst, cond=None):
    cnd = "3.0" if cond is None else cond
    amk("ptr", cnd, dst, P)

def jmp_abs(dst, cond=None):
    if cond is None:
        set_csr("ptr", dst, "2.0", P)
    else:
        mov(tmp(0), cond)
        shl(tmp(0), tmp(0), 1)
        amk("ptr", tmp(0), dst, P)

# -----------------------------------------------------------------------------
# --------- RTLink ------------------------------------------------------------
# -----------------------------------------------------------------------------

def pack_frame(flg, chn, adr, tag, pld):
    wcad = C_BASE.RTLK["W_CHN_ADR"]
    wnad = C_BASE.RTLK["W_NOD_ADR"]
    wtag = C_BASE.RTLK["W_TAG_LTN"]
    npld = C_BASE.RTLK["N_FRM_PLD"]
    nhdr = C_BASE.RTLK["N_BYT"] - 4*npld
    tmp = bit_concat((flg, 3), (chn, wcad), (adr, wnad), (tag, wtag)).to_bytes(nhdr,'big')
    rng = range(npld-1, -1, -1) if PL01 else range(npld)
    for i in rng:
        tmp += int(pld[i]).to_bytes(4,'big')
    return tmp

def unpack_frame(frm):
    wcad = C_BASE.RTLK["W_CHN_ADR"]
    wnad = C_BASE.RTLK["W_NOD_ADR"]
    wtag = C_BASE.RTLK["W_TAG_LTN"]
    npld = C_BASE.RTLK["N_FRM_PLD"]
    fhdr = int.from_bytes(frm[0:-(npld*4)], "big")
    fpld = frm[-(npld*4):]
    flg, chn, adr, tag = bit_split(fhdr, (3, wcad, wnad, wtag))
    pld = [0] * npld
    for i in range(npld):
        pld[i] = int.from_bytes(fpld[i*4:i*4+4], "big")
    if PL01:
        pld.reverse()
    return flg, chn, adr, tag, pld

def ich_dnld(payloads, start=0):
    cap = asm.core.CAP_ICH
    ln = len(payloads)
    if ln > cap:
        raise RuntimeError("Maximum instruction cache capacity exceeded.")
    chi('ica', 0)
    for i in range(ln):
        clo('ica', i + start)
        cli('icd', payloads[i])

@multi(asm)
def rtlk_send(flg, chn, adr, tag, tag_inc, pld, rng=None, align=None):
    # for instr. block, use tag_inc = -7
    if type(flg) is not int:
        flg = str(flg)
        if flg[0] != '$':
            typ = {"d": 0, "i": 1}[flg[0].lower()]
            srf = {"n": 0, "b": 1, "e": 2, "d": 3}[flg[1].lower()]
            flg = (typ<<2) + srf
    # R.$f0 = (flg<<20) + tag
    if type(flg) is int and type(tag) is int:
        mov(tmp(0), (flg<<20)+tag)
    elif flg == 0:
        mov(tmp(0), tag)
    else:
        if type(flg) is int:
            mov(tmp(0), flg << 20)
        else:
            shl(tmp(0), flg, 20)
        add(tmp(0), tmp(0), tmp(-1,tag))        
    # R.frm.dst = (chn<<2) + adr
    if type(chn) is int and type(adr) is int:
        mov('frm.dst', (chn<<20)+adr)
    elif chn == 0:
        mov('frm.dst', adr)
    else:
        if type(chn) is int:
            mov(tmp(-1), chn << 20)
        else:
            shl(tmp(-1), chn, 20)
        add(tmp(-1), tmp(-1), tmp(-2,adr))
        mov("frm.dst", tmp(-1))
    if rng is None:
        if type(pld) not in (tuple,list):
            pld = (pld,0)
        if len(pld) % 2 == 1:
            pld = list(pld) + [0]
        for i in range(0, len(pld), 2):
            mov("frm.tag", tmp(0))
            if tag_inc:
                add(tmp(0), tmp(0), tmp(-1,tag_inc))
            if PL01:
                mov("frm.pl1", pld[i+1])
                mov("frm.pl0", pld[i])
            else:
                mov("frm.pl0", pld[i])
                mov("frm.pl1", pld[i+1])
    else:
        if type(pld) in (tuple,list):
            pld = pld[0]
        align = align or 4
        if type(pld) not in (int,str):
            pld = str(pld)
        if type(rng) not in (tuple,list):
            rng = (rng,)
        if len(rng) == 1:
            start = 0
            stop = rng[0]
        else:
            start = rng[0]
            stop = rng[1]
        step = rng[2] if len(rng) > 2 else align
        dnld = getattr(asm, 'dnld', 1)
        if dnld:
            for_(tmp(1),(start,stop,step))
            for i in range(2):
                if PL01:
                    if type(pld) is str and pld[0] != '$':
                        mov('frm.pl1' if i&1 else tmp(2), pld+'.'+tmp(1))
                    else:
                        add(tmp(-1), tmp(1), tmp(-1,pld))
                        copy(['frm.pl1' if i&1 else tmp(2)], tmp(-1), align)
                    if i&1:
                        mov('frm.tag', tmp(0))
                        mov('frm.pl0', tmp(2))
                    else:
                        add(tmp(1), tmp(1), step)
                else:
                    if i&1:
                        mov('frm.tag', tmp(0))
                    if type(pld) is str and pld[0] != '$':
                        mov(f'frm.pl{i&1}', pld+'.'+tmp(1))
                    else:
                        add(tmp(-1), tmp(1), tmp(-1,pld))
                        copy([f'frm.pl{i&1}'], tmp(-1), align)
                    if not i&1:
                        add(tmp(1), tmp(1), step)
            if tag_inc:
                add(tmp(0), tmp(0), tmp(-1,tag_inc))
            end()
        else:
            if type(pld) is str and pld[0] == '$':
                add(tmp(1), pld, tmp(-1,start))
            while start < stop:
                for i in range(2):
                    if PL01:
                        if type(pld) is str and pld[0] != '$':
                            mov('frm.pl1' if i else tmp(2), pld+f'.&{start:x}')
                        else:
                            if type(pld) is str and pld[0] == '$':
                                add(tmp(1), tmp(1), tmp(-1,step))
                            else:
                                mov(tmp(1), pld+start)
                            copy(['frm.pl1' if i else tmp(2)], tmp(1), align)
                        if i:
                            mov('frm.tag', tmp(0))
                            mov('frm.pl0', tmp(2))
                    else:
                        if i:
                            mov('frm.tag', tmp(0))
                        if type(pld) is str and pld[0] != '$':
                            mov(f'frm.pl{i&1}', pld+f'.&{start:x}')
                        else:
                            if type(pld) is str and pld[0] == '$':
                                add(tmp(1), tmp(1), tmp(-1,step))
                            else:
                                mov(tmp(1), pld+start)
                            copy([f'frm.pl{i&1}'], tmp(1), align)
                    start += step
                if tag_inc:
                    add(tmp(0), tmp(0), tmp(-1,tag_inc))

@multi(asm)       
def intf_send(*pld, rng=None, align=None, oper=None, narg=None, info=None):
    intf = getattr(asm, 'intf', None)
    if intf is None:
        cfg = getattr(asm, 'cfg', None)
        if cfg is None:
            return
        intf = cfg.intf
    if info is not None:
        mov(tmp(1),'nex.adr')
        and_(tmp(1),tmp(1),tmp(-1,0xffff))
        add(tmp(1),tmp(1),tmp(-1,info<<20))
        return rtlk_send(4, intf.loc_chn, intf.nod_adr, 0, 0, [tmp(1),pld[0]])
    if len(pld) > 0:
        rtlk_send(0, intf.loc_chn, intf.nod_adr, 'nex.adr', 0, pld, rng, align)
    if oper is not None:
        mov(tmp(1),'nex.adr')
        and_(tmp(1),tmp(1),tmp(-1,0xffff))
        if narg is not None:
            add(tmp(1),tmp(1),tmp(-1,narg<<16))
        rtlk_send(0, intf.loc_chn, intf.nod_adr, 0xffff, 0, [tmp(1),oper])

def intf_run(func,sync=True):
    core = asm.core
    intf = getattr(asm, 'intf', None)
    if intf is None:
        cfg = getattr(asm, 'cfg', None)
        if cfg is None:
            return lambda *args:None
        intf = cfg.intf
        core = cfg.core
    oper = intf.oper.get((id(func)<<1)|sync,None)
    if oper is None:
        def cb(buf,cfg):
            if sync:
                with asm:
                    asm.dnld = 0
                    asm.core = core
                    func(buf)
                    clr_bit("exc", "1.0", P)
                    cfg(asm[:],rply=0)
            else:
                cfg.core = core
                cfg(func,dnld=0)(buf)
        oper = len(intf.oper) + 1
        intf.oper[(id(func)<<1)|sync] = oper
        intf.oper[oper] = cb
    def wrap(*args,**kwargs):
        narg = kwargs.get('narg',None)
        if narg is None:
            narg = len(args)
            if narg&1:
                narg += 1
            kwargs['narg'] = narg
        intf_send(*args,**kwargs,oper=oper)
        if sync:
            set_bit("exc", "1.0", P)
    return wrap

intf_run_async = lambda func: intf_run(func,sync=False)

@multi(asm)
def scp_read(adr, dst):
    mov("scp.mem", adr)
    nop(1, P)
    mov(dst, "scp")

@multi(asm)
def wait_rtlk_trig(typ, cod, tout=None):
    mov({"c": "scp.cdm", "t": "scp.tgm"}[typ], cod)
    set_bit("scp", "2.F")
    if tout is not None:
        flg = "6.0"
        set_csr("tim", tout, "2.0")
    else:
        flg = "2.0"
    set_bit("rsm", flg)
    clr_bit("exc", "2.0", H)
    clr_bit("rsm", flg)
    clr_bit("scp", "2.F")

@multi(asm)
def send_trig_code(flg, adr, ltn, code):
    with asm as trg:
        sfs("scp", "cod")
        if isinstance(code, int):
            clo("scp", code)
        else:
            amk("scp", "$01", code)
    rtlk_send(flg, 0, adr, ltn, 0, trg[:])

# -----------------------------------------------------------------------------
# --------- Debug Helper ------------------------------------------------------
# -----------------------------------------------------------------------------

class ich_cfg:
    def __init__(self, fn, core=None):
        self.fn = fn
        self.core = core
        self.stat = 0

    def __call__(self, *args, **kwargs):
        if self.stat == 0:
            self.func = args[0]
            self.stat = 1
            return self
        self.stat = 0
        if self.core is None:
            self.core = asm.core
        with asm:
            asm.core = self.core
            init01()
            self.func(*args, **kwargs)
            nop(2, H)
            ram = "@00000000\n"
            for ins in asm[:]:
                ram += f"{ins:08X}\n"
            with open(self.fn, "w") as f:
                f.write(ram)

class run_cfg:
    def __init__(self, intf, dst, mon=None, chn=0, flg="in", tag=0, core=None):
        if isinstance(flg, str):
            typ = {"d": 0, "i": 1}[flg[0].lower()]
            srf = {"n": 0, "b": 1, "e": 2, "d": 3}[flg[1].lower()]
            flg = typ * 4 + srf
        self.intf = intf
        self.flg = flg
        self.chn = chn
        self.dst = dst
        self.mon = dst if mon is None else mon
        self.tag = tag
        self.core = core
        self.stat = 0

    def __call__(self, *args, **kwargs):
        if self.stat == 0:
            self.func = args[0]
            self.dnld = kwargs["dnld"] if "dnld" in kwargs else 1
            self.rply = kwargs["rply"] if "rply" in kwargs else 1
            self.dst  = kwargs["dst"] if "dst" in kwargs else self.dst
            self.mon  = kwargs["mon"] if "mon" in kwargs else self.mon
            self.tout = kwargs["tout"] if "tout" in kwargs else 1.0
            self.proc = kwargs["proc"] if "proc" in kwargs else None
            if type(self.func) is not table and callable(self.func):
                self.stat = 1
                return self
        self.stat = 0
        if not callable(self.func):
            flw = self.func
        else:
            with asm as flw:
                asm.intf = self.intf
                asm.tout = self.tout
                asm.proc = self.proc
                if type(self.func) is table:
                    nodes = getattr(self.func,'multi',None)
                    if nodes is None:
                        asm.dnld = self.dnld
                        asm(*self.func[:],**self.func.__dict__)
                    else:
                        asm.multi = nodes
                        for adr in nodes:
                            asm[str(adr)] = self.func[str(adr)].copy()
                            if getattr(asm[str(adr)],'dnld',None) is None:
                                asm[str(adr)].dnld = self.dnld
                else:
                    if self.core is not None:
                        asm.core = self.core
                    asm.dnld = self.dnld
                    res = self.func(*args, **kwargs)
                    if len(asm) == 0:
                        return res
                finish()
        with self.intf:
            nodes = getattr(flw,'multi',None)
            if nodes is None:
                rply = getattr(flw,'rply',getattr(flw,'dnld',self.rply))
                for adr in self.dst:
                    self.intf.write(self.flg, self.chn, adr, self.tag, flw[:])
            else:
                flws = flw
                rply = 0
                for i in range(len(self.dst)):
                    flw = flws[str(nodes[i])]
                    rply += getattr(flw,'rply',flw.dnld and self.rply)
                    self.intf.write(self.flg, self.chn, self.dst[i], self.tag, flw[:])
            if (self.intf.thread and self.intf.thread.running) or not rply:
                return None
            tout = getattr(flw,'tout',self.tout)
            res = self.intf.monitor(self.mon, round(tout * 10))
            proc = getattr(flw,'proc',self.proc)
            if proc is None:
                return None if len(res) == 0 else res
            else:
                ret = dict()
                for k, v in res.items():
                    ret[k] = proc(k, v)
                return ret
        
class assembler:
    def __init__(self, cfg=None, multi=None):
        self.cfg = cfg
        core = cfg and cfg.core or asm.core
        intf = cfg and cfg.intf or getattr(asm,'intf',None)
        with asm as self.asm:
            if multi is None:
                setup(core)
                asm.intf = intf
            else:
                nodes = []
                cores = []
                for i in multi:
                    if type(i) in (tuple,list):
                        nodes.append(str(i[0]))
                        cores.append(i[1])
                    else:
                        nodes.append(str(i))
                        cores.append(core)
                asm.multi = nodes
                for i in range(len(nodes)):
                    name = nodes[i]
                    setup[name](cores[i])
                    asm[name].intf = intf
                    self[name] = asm < asm[name]
                        
    def __getitem__(self, key):
        return getattr(self, str(key))
    
    def __setitem__(self, key, val):
        return setattr(self, str(key), val)
    
    def run(self, disa=False):
        if disa:
            multi = getattr(self.asm,'multi',None)
            if multi is None:
                print(disassembler()(self.asm,0))
            else:
                for i in multi:
                    print(i)
                    print(disassembler()(self.asm[str(i)],0))
        if self.cfg and self.cfg.intf:
            return self.cfg(self.asm)
    
    def clear(self):
        multi = getattr(self.asm,'multi',None)
        if multi is None:
            self.asm.clear()
        else:
            for i in multi:
                self.asm[str(i)].clear()
        return self

    def __enter__(self):
        self.asm = asm <= self.asm

    def __exit__(self, exc_type, exc_value, traceback):
        self.asm = asm <= self.asm

    def __call__(self, *args, **kwargs):
        multi = getattr(self.asm,'multi',None)
        if multi is None:
            if len(args) < 1:
                return self
            with self:
                args[0](*args[1:],**kwargs)
        else:
            if len(args) < 2:
                return self
            if args[0] is None:
                with self:
                    args[1](*args[2:],**kwargs)
            else:
                with self[args[0]]:
                    args[1](*args[2:],**kwargs)
        return self
                    
def core_run(func):
    def wrap(*args, **kwargs):
        cfg = getattr(asm,'cfg',None)
        return func(*args, **kwargs) if cfg is None else cfg(func)(*args,**kwargs)
    return wrap

@core_run
def core_read(*args, **kwargs):
    asm.dnld = 0
    asm.rply = 1
    proc = kwargs.get('proc',None)
    if proc is not None:
        kwargs.pop('proc')
        asm.proc = lambda a, x: proc(x)
    intf_send(*args,**kwargs,oper=0)

@core_run
def core_write(dst, val, align=4):
    asm.dnld = 0
    copy(dst, val, align=align)

if __name__ == '__main__':
    pass
