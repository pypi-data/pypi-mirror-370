from . import *

def select(r, a, b, c):
    neq('$ff', c, '$00')
    and_(a, '$ff', a)
    ian(b, '$ff', b)
    bor(r, a, b)

def global_get(r, idx=0):
    idx = int(idx)
    if idx < 0x1C:
        mov(r, f'${(4+idx):02X}')
    else:
        idx -= 0x1C
        mov('$02', 'stk')
        mov('stk', idx, P)
        mov('$03', '$20')
        mov('stk', '$02', P)
        mov(r, '$03')

def global_set(a, idx=0):
    idx = int(idx)
    if idx < 0x1C:
        mov(f'${(4+idx):02X}', a)
    else:
        idx -= 0x1C
        mov('$02', 'stk')
        mov('$03', a)
        mov('stk', idx, P)
        mov('$20', '$03')
        mov('stk', '$02', P)

def i32_load(r, a, align=4, offset=0, size=4):
    if offset != 0:
        mov('$ff', offset)
        add('$ff', '$ff', a)
        a = '$ff'
    amk('dcf', '3.f', f'{size&3}.f')
    mov('dca', a, P)
    nop(3)
    mov(r, 'dcd')

def i32_load8_u(r, a, align=1, offset=0):
    i32_load(r, a, 1, offset, 1)
    shl(r, r, 24)
    shr(r, r, 24)

def i32_load8_s(r, a, align=1, offset=0):
    i32_load(r, a, 1, offset, 1)
    shl(r, r, 24)
    sar(r, r, 24)

def i32_load16_u(r, a, align=2, offset=0):
    if align == 0:
        if offset != 0:
            mov('$ff', offset)
            add('$ff', '$ff', a)
            a = '$ff'
        amk('dcf', '3.f', '1.f')
        mov('dca', a, P)
        nop(3)
        mov(r, 'dcd')
        shl(r, r, 24)
        shr(r, r, 24)
        sub('$ff', a, '$01')
        amk('dcf', '3.f', '1.f')
        mov('dca', '$ff')
        nop(3)
        mov('$ff', 'dcd')
        shl('$ff', '$ff', 24)
        shr('$ff', '$ff', 16)
        bor(r, r, '$ff')
    else:
        i32_load(r, a, 2, offset, 2)

def i32_load16_s(r, a, align=2, offset=0):
    i32_load(r, a, 2, offset, 2)
    shl(r, r, 16)
    sar(r, r, 16)

def i32_store(a, b, align=4, offset=0, size=4):
    if offset != 0:
        mov('$ff', offset)
        add('$ff', '$ff', a)
        a = '$ff'
    amk('dcf', '3.f', f'{size&3}.f')
    mov('dca', a)
    mov('dcd', b)

def i32_store8(a, b, align=1, offset=0):
    i32_store(a, b, 1, offset, 1)

def i32_store16(a, b, align=2, offset=0):
    if align == 0:
        if offset != 0:
            mov('$ff', offset)
            add('$ff', '$ff', a)
            a = '$ff'
        amk('dcf', '3.f', '1.f')
        mov('dca', a)
        amk('dca', '2.0', a)
        mov('dcd', b)
        sub('$ff', a, '$01')
        shr('$fe', b, 8)
        amk('dcf', '3.f', '1.f')
        mov('dca', '$ff')
        mov('dcd', '$fe')
    else:
        i32_store(a, b, 2, offset, 2)

i32_const = mov

def i32_eqz(r, a):
    equ(r, a, '$00')
    sgn(r, '$01', r)

def i32_eq(r, a, b):
    equ(r, a, b)
    sgn(r, '$01', r)
    
def i32_ne(r, a, b):
    neq(r, a, b)
    sgn(r, '$01', r)

def i32_lt_s(r, a, b):
    lst(r, a, b)
    sgn(r, '$01', r)

def i32_lt_u(r, a, b):
    csb(r, a, b)
    sgn(r, '$01', r)

def i32_le_s(r, a, b):
    lse(r, a, b)
    sgn(r, '$01', r)

def i32_le_u(r, a, b):
    csb(r, b, a)
    ian(r, r, '$01')
    sgn(r, '$01', r)

def i32_gt_s(r, a, b):
    lst(r, b, a)
    sgn(r, '$01', r)

def i32_gt_u(r, a, b):
    csb(r, b, a)
    sgn(r, '$01', r)

def i32_ge_s(r, a, b):
    lse(r, b, a)
    sgn(r, '$01', r)

def i32_ge_u(r, a, b):
    csb(r, a, b)
    ian(r, r, '$01')
    sgn(r, '$01', r)

i32_add = add
i32_sub = sub
i32_mul = mul
#def i32_div_s(r, a, b):
#    pass
i32_div_u = div_u
#def i32_rem_s(r, a, b):
#    pass
i32_rem_u = rem_u
i32_and = and_
i32_or = bor
i32_xor = xor
i32_shl = shl
i32_shr_s = sar
i32_shr_u = shr
i32_rotl = rol

try:        
    from pywasm import binary,instruction
except:
    pass
    
class wasm2reg:
    def __init__(self, module, imps=None):
        if type(module) is str:
            with open(module, 'rb') as f:
                module = binary.Module.from_reader(f)
        self.module = module
        imps = imps if imps else {}
        self.funcs = []
        for e in module.import_list:
            if e.module not in imps or e.name not in imps[e.module]:
                raise Exception(f'RegVM: missing import {e.module}.{e.name}')
            if isinstance(e.desc, binary.TypeIndex):
                self.funcs.append([e.desc,imps[e.module][e.name]])
        self.ext_size = len(self.funcs)
        for i in range(len(module.function_list)):
            func = module.function_list[i]
            self.funcs.append([func.type_index,func])
        for i in range(len(module.function_list)):
            self.transpile(i + self.ext_size)
        self.exps = {}
        for e in self.module.export_list:
            if isinstance(e.desc, binary.FunctionIndex):
                self.exps[e.name] = int(e.desc)
                self.exps[int(e.desc)] = e.name
        self.mem = bytearray(65536*(module.memory_list[0].type.limits.n))
        for data_segment in module.data_list:
            offset = int(data_segment.offset.data[0].args[0])
            init = data_segment.init
            if data_segment.memory_index == 0:
                self.mem[offset:offset+len(init)] = init
        
    def transpile(self, name):
        func_type, func = self.funcs[name]
        self.code = []
        func_type = self.module.type_list[func_type]
        arg_size = len(func_type.args.data)
        init_size = 0x20 + arg_size + 2 + len(func.local_list)
        self.used = list(range(init_size))
        last_return = binary.Instruction()
        last_return.opcode = 0x0f
        instrs = func.expr.data + [last_return]
        for pc in range(len(instrs)):
            self.opcode,self.oparg = instrs[pc].opcode,instrs[pc].args.copy()
            #print(f'{name}:{pc}\t', instrs[pc])
            if self.opcode in (0x20,0x21,0x22) and self.oparg[0] >= arg_size: # local_get/set/tee
                self.oparg[0] += 2
            if self.opcode == 0x02: # block
                self.oparg += [func.expr.position[pc][1]]
                self.oper(0,0)
            elif self.opcode == 0x0e: # br_table
                self.oparg = self.oparg[0] + [self.oparg[1]]
                self.oper(1,0)
            elif self.opcode == 0x0f: # return
                self.oparg.append(arg_size)
                #if size != len(func_type.rets.data):
                #    raise
                self.oper(len(self.used)-init_size,0)
            elif self.opcode == 0x10: # call
                call_type = self.module.type_list[self.funcs[self.oparg[0]][0]]
                self.used.append(len(self.used))
                self.oper(1+len(call_type.args.data),len(call_type.rets.data))
            elif self.opcode == 0x11: # call_indirect
                call_type = self.module.type_list[self.oparg[0]]
                self.used.append(len(self.used))
                self.oper(2+len(call_type.args.data),len(call_type.rets.data))
            elif self.opcode in (0x20,0x23,0x3f) or 0x41 <= self.opcode <= 0x44:
                self.oper(0,1)
            elif self.opcode in (0x0d,0x1a,0x21,0x24):
                self.oper(1,0)
            elif self.opcode in (0x1b,) or 0x36 <= self.opcode <= 0x3e:
                if self.opcode == 0x1b:
                    self.oper(3,1)
                else:
                    self.oper(2,0)
            elif 0x46 <= self.opcode <= 0xa6 and not (self.opcode in (0x50,0x67,0x68,0x69,0x79,0x7a,0x7b) or 0x8b <= self.opcode <= 0x91 or 0x99 <= self.opcode <= 0x9f):
                self.oper(2,1)
            else:
                if self.opcode <= 0x0c:
                    self.oper(0,0)
                else:
                    self.oper(1,1)
        self.funcs[name] = [self.funcs[name][0]] + self.code
    
    def oper(self, pop, push):
        if pop > 0:
            args = self.used[-pop:]
            self.used = self.used[:-pop]
        else:
            args = []
        for i in range(push):
            self.used.append(len(self.used))
        rets = [] if push == 0 else self.used[-push:]
        instr = [self.opcode,self.oparg,args,rets]
        self.code.append(instr)
        #print('\t',self.line(instr))
    
    def line(self, instr):
        opcode,oparg,args,rets = instr 
        r = ''
        if len(rets) > 0:
            r += ','.join([f'${i:02X}' for i in rets]) + ' = '
        r += instruction.opcode[opcode][0]
        if len(oparg) > 0:
            r += '(' + ','.join([str(int(i)) for i in oparg]) + ')'
        r += ' ' + ','.join([f'${i:02X}' for i in args])
        return r

    def __repr__(self):
        r = []            
        for i in range(len(self.funcs)):
            func = self.funcs[i]
            func_type = self.module.type_list[func[0]]
            rets = func_type.rets.data
            args = [str(i) for i in func_type.args.data]
            if i < self.ext_size:
                r.append(f'{rets} = @{i}({",".join(args)}) {self.funcs[i][1]}')
            else:
                r.append(f'{rets} = @{i}({",".join(args)})' + ' {')
                for instr in func[1:]:
                    r.append(self.line(instr))
                r.append('}')
        return '\n'.join(r)
                
class wasm2rtmq:
    def __init__(self, module, imps=None):
        if type(module) is str:
            with open(module, 'rb') as f:
                module = binary.Module.from_reader(f)
        self.module = module
        self.vm = wasm2reg(self.module, imps)
        self.code = []
        self.bubble = None
        self.CLO('STK',0)
        self.GLO('$00',0)
        self.GLO('$01',-1)
        self.CHI('DCF',0)
        self.CHI('DCA',0)
        self.global_size = len(self.module.global_list)
        for i in range(self.global_size):
            rd = f'${(0x04+i):02X}'
            val = self.module.global_list[i].expr.data[0].args[0]
            self.GLO(rd, val)
            if val != to_signed(val,20):
                self.GHI(rd, val)
        if self.global_size > 0x1C:
            self.CLO('STK',self.global_size - 0x1C)
        for data_segment in self.module.data_list:
            if data_segment.memory_index == 0:
                offset = int(data_segment.offset.data[0].args[0])
                size = len(data_segment.init)
                data = bytearray(data_segment.init)
                if size & 1:
                    data = data + bytearray(1)
                    size += 1
                self.CHI('DCF', 2<<30)
                self.CLO('DCF', size>>1)
                self.CLO('DCA', offset)
                for i in range(0, size, 2):
                    val = int.from_bytes(data[i:(i+2)], 'little')
                    self.CLO('DCD', val)
                self.CHI('DCF',0)
        self.init = self.code
        self.funcs = self.vm.funcs
        self.ext_size = self.vm.ext_size
        self.exps = self.vm.exps
        self.pos = [[] for i in range(len(self.funcs))]
        for i in range(len(self.funcs)):
            self.transpile(i)
        self.pc = 0
        self.code = []
        for i in range(len(self.funcs)):
            self.code.append(self.pc)
            self.pc += len(self.funcs[i]) - 1
        for i in range(len(self.funcs)):
            for pos in self.pos[i]:
                self.funcs[pos[0]][1+pos[1]][-1] = '#' + self.exps.get(i,str(self.code[i]))
            self.pos[i] = self.code[i]
        for i in range(len(self.funcs)):
            self.code += self.funcs[i][1:]
            
    def transpile(self, name):
        func = self.funcs[name]
        func_type = self.module.type_list[func[0]]
        self.name = name
        #print(f'{func_type.rets.data} = @{self.exps.get(name,name)}({",".join([str(i) for i in func_type.args.data])})')      
        self.code = []
        self.bubble = None
        arg_size = len(func_type.args.data)
        self.SUB(f'${(0x20+arg_size):02X}', '$00', f'${(0x20+arg_size):02X}')
        self.CSR(f'${(0x21+arg_size):02X}','LNK')
        #print('\t', self.line(self.code[0]))#,'\t', f'{name}:{0}')
        self.pc = 1
        self.label = []
        if name < self.ext_size:
            if callable(func[1]):
                func[1](self)
            else:
                self.code = []
                self(func[1])
        else:
            for i in range(len(func)-1):
                instr = func[1+i]
                line = self.vm.line(instr)
                #print(f'{name}:{i}\t', line)
                opcode,oparg,args,rets = instr
                opname = instruction.opcode[opcode][0].replace('.','_')
                if opname in ('return',):
                    opname += '_'
                oper = getattr(self,opname,None)
                if callable(oper):
                    oper(oparg,args,rets)
                else:
                    oper = globals().get(opname,None)
                    if callable(oper):
                        #print(opname, *rets, *args, *oparg)
                        self(disassembler()(oper)(*map(lambda i:f'${i:02X}',rets+args),*oparg))
                    else:
                        raise NotImplementedError(f'{name}:{i}\t{line}')
                #for j in range(self.pc,len(self.code)):
                    #print('\t',self.line(self.code[j]))#,'\t',f'{name}:{j}')
                self.pc = len(self.code)
        self.funcs[name] = [func[0]] + self.code
    
    def __call__(self, *args):
        if len(args) == 1:
            code = args[0]
            if type(code) is str:
                code = code.strip().split('\n')            
            for line in code:
                if type(line) is str:
                    self(*line.strip().split(' '))
                elif type(line) is int:
                    self.code.append((hex(line),))
            return
        for i in args[3:]:
            if self.bubble == i:
                self.code.append(['NOP','-'])
                break
        self.code.append(list(args))
        self.bubble = args[2] if len(args) > 2 and args[1] == '-' else None
        
    def line(self, instr):
        return ' '.join([str(i) for i in instr])
        
    def __repr__(self):
        r = []
        for instr in self.init:
            r.append(self.line(instr))
        r.append('GLO - $20 0')
        r.append('CLO P PTR #_start')
        start = False     
        for i in range(len(self.funcs)):
            func = self.funcs[i]
            types = self.module.type_list[func[0]]
            name = self.exps.get(i,self.pos[i])
            r.append(f'#{name}:')
            rets = types.rets.data
            args = [str(i) for i in types.args.data]
            r.append(f'%{rets} = @{i}({",".join(args)})' + ' [')
            for instr in func[1:]:
                r.append(self.line(instr))
            r.append('%]')
        return '\n'.join(r)
    
    def NOP(self,n=1,hp='-'):
        for i in range(n):
            self('NOP',hp)
    def SFS(self,rd,r0,hp='-'):
        self('SFS',hp,rd,r0)
    def CHI(self,rd,r0,hp='-'):
        self('CHI',hp,rd,r0)
    def CLO(self,rd,r0,hp='-'):
        self('CLO',hp,rd,r0)
    def AMK(self,rd,r0,r1,hp='-'):
        self('AMK',hp,rd,r0,r1)
    def AND(self,rd,r0,r1,hp='-'):
        self('AND',hp,rd,r0,r1)
    def IAN(self,rd,r0,r1,hp='-'):
        self('IAN',hp,rd,r0,r1)
    def BOR(self,rd,r0,r1,hp='-'):
        self('BOR',hp,rd,r0,r1)
    def XOR(self,rd,r0,r1,hp='-'):
        self('XOR',hp,rd,r0,r1)
    def CSR(self,rd,r0,hp='-'):
        self('CSR',hp,rd,r0)
    def GHI(self,rd,r0,hp='-'):
        self('GHI',hp,rd,r0)
    def SGN(self,rd,r0,r1,hp='-'):
        self('SGN',hp,rd,r0,r1)
    def OPL(self,rd,r0,hp='-'):
        self('OPL',hp,rd,r0)
    def PLO(self,rd,hp='-'):
        self('PLO',hp,rd)
    def PHI(self,rd,hp='-'):
        self('PHI',hp,rd)
    def DIV(self,rd,hp='-'):
        self('DIV',hp,rd)
    def MOD(self,rd,hp='-'):
        self('MOD',hp,rd)
    def GLO(self,rd,r0,hp='-'):
        self('GLO',hp,rd,r0)
    def ADD(self,rd,r0,r1,hp='-'):
        self('ADD',hp,rd,r0,r1)
    def SUB(self,rd,r0,r1,hp='-'):
        self('SUB',hp,rd,r0,r1)
    def CAD(self,rd,r0,r1,hp='-'):
        self('CAD',hp,rd,r0,r1)
    def CSB(self,rd,r0,r1,hp='-'):
        self('CSB',hp,rd,r0,r1)
    def NEQ(self,rd,r0,r1,hp='-'):
        self('NEQ',hp,rd,r0,r1)
    def EQU(self,rd,r0,r1,hp='-'):
        self('EQU',hp,rd,r0,r1)
    def LST(self,rd,r0,r1,hp='-'):
        self('LST',hp,rd,r0,r1)
    def LSE(self,rd,r0,r1,hp='-'):
        self('LSE',hp,rd,r0,r1)
    def SHL(self,rd,r0,r1,hp='-'):
        self('SHL',hp,rd,r0,r1)
    def SHR(self,rd,r0,r1,hp='-'):
        self('SHR',hp,rd,r0,r1)
    def ROL(self,rd,r0,r1,hp='-'):
        self('ROL',hp,rd,r0,r1)
    def SAR(self,rd,r0,r1,hp='-'):
        self('SAR',hp,rd,r0,r1)
                
    def MOV(self,rd,r1):
        if rd != r1:
            self.ADD(rd,r1,'$00')
    
    def unreachable(self,oparg,args,rets):
        pass
    def nop(self,oparg,args,rets):
        pass

    # block ... drop       
    def block(self,oparg,args,rets):
        self.label.insert(0,[])
    def loop(self,oparg,args,rets):
        self.label.insert(0,self.pc)
    def end(self,oparg,args,rets):
        if len(self.label) == 0:
            return
        pos = self.label[0]
        self.label = self.label[1:]
        if type(pos) is list:
            for i in pos:
                self.code[i][-1] += self.pc
    def br(self,oparg,args,rets):
        pos = self.label[oparg[0]]
        if type(pos) is list:
            pos.append(self.pc)
            self.GLO('$FF',-self.pc-2)
        else:
            self.GLO('$FF',pos-self.pc-2)
        #self.NOP()
        self.AMK('PTR','3.0','$FF','P')
    def br_if(self,oparg,args,rets):
        pos = self.label[oparg[0]]
        if type(pos) is list:
            pos.append(self.pc)
            self.GLO('$FF',-self.pc-3)
        else:
            self.GLO('$FF',pos-self.pc-3)
        self.NEQ('$FE',f'${args[0]:02X}','$00')
        #self.NOP()
        self.AMK('PTR','$FE','$FF','P')
    def br_table(self,oparg,args,rets):
        self.GLO('$FF',len(oparg)-2)
        self.GLO('$FE',3*len(oparg)+5)
        self.CSB('$FF','$FF',f'${args[0]:02X}')
        #self.NOP()
        self.AMK('PTR','$FF','$FE','P')
        self.ADD('$FF',f'${args[0]:02X}',f'${args[0]:02X}')
        #self.NOP()
        self.ADD('$FF','$FF',f'${args[0]:02X}')
        #self.NOP()
        self.SUB('$FF','$FF','$01')
        #self.NOP()
        self.AMK('PTR','3.0','$FF','P')
        for i in range(len(oparg)):
            pos = self.label[oparg[i]]
            if type(pos) is list:
                pos.append(self.pc+12+3*i)
                self.GLO('$FF',-self.pc-14-3*i)
            else:
                self.GLO('$FF',pos-self.pc-14-3*i)
            #self.NOP()
            self.AMK('PTR','3.0','$FF','P')
    def return_(self,oparg,args,rets):
        arg_size = oparg[0]
        stk = f'${(0x20+arg_size):02X}'
        lnk = f'${(0x21+arg_size):02X}'
        if len(args) > arg_size:
            self.MOV('$FF', stk)
            stk = '$FF'
            if len(args) > arg_size + 1:
                self.MOV('$FE', lnk)
                lnk = '$FE'
        for i in range(len(args)):
            self.MOV(f'${(0x20+i):02X}', f'${args[i]:02X}')
        self.AMK('STK', '3.0', stk)
        self.AMK('PTR', '2.0', lnk, 'P')
    def call(self,oparg,args,rets):
        pos = args[0]-0x20 if len(args) > 0 else 0
        self.GLO(f'${(0x20+pos+len(args)-1):02X}', pos)
        if pos > 0:
            self.AMK('STK', '3.0', pos)
        self.pos[oparg[0]].append((self.name,self.pc+(2 if pos>0 else 1)))
        self.CLO('PTR',f'@{int(oparg[0])}','P')
        for i in range(len(rets)):
            self.MOV(f'${rets[i]:02X}',f'${(0x20+pos+i):02X}')
    def drop(self,oparg,args,rets):
        pass
    
    # select
    # ...

    def local_get(self,oparg,args,rets):
        self.MOV(f'${rets[0]:02X}',f'${(0x20+oparg[0]):02X}')
    def local_set(self,oparg,args,rets):
        self.MOV(f'${(0x20+oparg[0]):02X}',f'${args[0]:02X}')
    def local_tee(self,oparg,args,rets):
        self.MOV(f'${(0x20+oparg[0]):02X}',f'${args[0]:02X}')

    # global_get ... i32_store16
    # ...

    def memory_size(self,oparg,args,rets):
        self.SUB(f'${rets[0]:02X}','$00','$01')
    def memory_grow(self,oparg,args,rets):
        self.MOV(f'${rets[0]:02X}','$01')

    # i32_const ... i32_rotl
    # ...

if __name__ == '__main__':
    import sys
    def getch(vm):
        vm.AMK('RSM','8.0','8.0','H')
        vm.CSR('$21','TRM')
        vm.AMK('RSM','8.0','0.0')
        vm.return_([0],[0x21],[])
    def putch(vm):
        vm.AMK('RSM','1.2','1.2','H')
        if True:
            vm('''
            SFS - FRM DST
            CHI - FRM 0x10ffff
            CLO - FRM 0x10ffff
            SFS - FRM TAG
            AMK - FRM $01 $00
            SFS - FRM PL1
            AMK - FRM $01 $00
            SFS - FRM PL0
            AMK - FRM $01 $20
            ''')
        else:
            with asm:
                sfs('frm','dst')
                chi('frm',0x10ffff)
                clo('frm',0x10ffff)
                sfs('frm','tag')
                amk('frm','$01','$00')
                sfs('frm','pl1')
                amk('frm','$01','$00')
                sfs('frm','pl0')
                amk('frm','$01','$20')
                vm(asm[:])
        vm.AMK('RSM','1.2','0.2')
        vm.return_([1],[],[])
    vm = wasm2reg(sys.argv[1],{'env':{'getch':getch,'putch':putch}})
    print(vm)
    vm = wasm2rtmq(sys.argv[1],{'env':{'getch':getch,'putch':putch}})
    with open(sys.argv[1].replace('.wasm','.txt'),'w') as f:
        f.write(repr(vm))
               