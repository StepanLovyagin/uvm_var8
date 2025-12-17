import argparse
import sys
import struct
import xml.etree.ElementTree as ET
import xml.dom.minidom

OP_LOAD_CONST = 60
OP_READ_MEM   = 12
OP_WRITE_MEM  = 28
OP_MUL        = 94

class VirtualMachine:
    def __init__(self, data_size=16384):
        self.data_memory = [0] * data_size
        self.instruction_memory = bytearray()
        self.stack = []
        self.pc = 0

    def load_program(self, path):
        try:
            with open(path, 'rb') as f:
                self.instruction_memory = f.read()
            self.pc = 0
        except FileNotFoundError:
            print(f"Ошибка: Файл {path} не найден.")
            sys.exit(1)

    def execute(self):
        print("Запуск интерпретации...")
        while self.pc < len(self.instruction_memory):
            if self.pc + 4 > len(self.instruction_memory): break
            
            val = struct.unpack("<I", self.instruction_memory[self.pc:self.pc+4])[0]
            self.pc += 4
            
            opcode = val & 0xFF
            operand = val >> 8
            
            try:
                if opcode == OP_LOAD_CONST:
                    self.stack.append(operand & 0x7FFFF)
                
                elif opcode == OP_READ_MEM:
                    addr = operand & 0x3FFF
                    self.stack.append(self.data_memory[addr])
                
                elif opcode == OP_WRITE_MEM:
                    value = self.stack.pop()
                    addr = self.stack.pop()
                    self.data_memory[addr] = value
                
                elif opcode == OP_MUL:
                    addr = operand & 0x3FFF
                    op2 = self.stack.pop()
                    op1 = self.data_memory[addr]
                    self.stack.append(op1 * op2)
                
                else:
                    print(f"Runtime Error: Unknown opcode {opcode}")
                    break
            except IndexError:
                print("Runtime Error: Memory/Stack access violation")
                sys.exit(1)
        print("Интерпретация завершена.")

    def dump_memory(self, path, start, end):
        root = ET.Element("memory")
        safe_end = min(len(self.data_memory), end)
        for i in range(start, safe_end):
            cell = ET.SubElement(root, "cell")
            cell.set("address", str(i))
            cell.text = str(self.data_memory[i])
        
        xml_str = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        print(f"Дамп сохранен: {path}")

def parse_range(s):
    try:
        parts = s.replace('-', ':').split(':')
        return int(parts[0]), int(parts[1])
    except:
        return 0, 16

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("bin_file")
    parser.add_argument("res_file")
    parser.add_argument("range")
    args = parser.parse_args()
    
    start, end = parse_range(args.range)
    vm = VirtualMachine()
    vm.load_program(args.bin_file)
    vm.execute()
    vm.dump_memory(args.res_file, start, end)