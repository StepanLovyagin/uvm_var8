import argparse
import struct
import json
import sys
import csv

#спецификация команд
OPCODES = {
    "LOAD_CONST": {"code": 60, "b_bits": 19},
    "READ_MEM":   {"code": 12, "b_bits": 14},
    "WRITE_MEM":  {"code": 28, "b_bits": 0},
    "MUL":        {"code": 94, "b_bits": 14}
}

def parse_csv_to_ir(input_path):
    ir = []
    with open(input_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        rows = list(reader)


    for i, row in enumerate(rows):
        if not row: continue
        cmd_name = row[0].strip().upper()
        
        if cmd_name not in OPCODES or cmd_name.startswith(';'):
            continue

        param_str = row[1].strip() if len(row) > 1 else "0"
        if not param_str or param_str.startswith(';'): param_str = "0"
        
        try:
            param_str = param_str.split(';')[0].strip()
            operand = int(param_str)
        except ValueError:
            print(f"Ошибка в строке {i+1}: Неверный операнд '{row[1]}'")
            sys.exit(1)

        spec = OPCODES[cmd_name]
        max_b = (1 << spec["b_bits"]) if spec["b_bits"] > 0 else 0
        if spec["b_bits"] > 0 and not (0 <= operand < max_b):
             print(f"Ошибка: Операнд {operand} выходит за пределы {spec['b_bits']} бит")
             sys.exit(1)
        
        ir.append({
            "index": i,
            "cmd": cmd_name,
            "opcode": spec["code"],
            "operand": operand
        })
    return ir

def generate_binary(ir):
    binary_data = bytearray()
    for instr in ir:
        val = instr["opcode"] | (instr["operand"] << 8)
        binary_data.extend(struct.pack("<I", val))
    return binary_data

def write_binary_file(output_path, binary_data):
    try:
        with open(output_path, 'wb') as f:
            f.write(binary_data)
        print(f"Сборка: {output_path} ({len(binary_data)} байт)")
    except OSError as e:
        print(f"Ошибка записи: {e}")
        sys.exit(1)

def print_test_output(ir):
    for instr in ir:
        opcode = instr["opcode"]
        operand = instr["operand"]
        val = opcode | (operand << 8)
        bytes_le = struct.pack("<I", val)
        hex_bytes = ", ".join(f"0x{b:02X}" for b in bytes_le)

        if instr["cmd"] == "WRITE_MEM":
            print(f"Тест (A={opcode}):")
        else:
            print(f"Тест (A={opcode}, B={operand}):")
        print(hex_bytes)
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("--test", action="store_true")

    args = parser.parse_args()

    ir = parse_csv_to_ir(args.input_file)
    bin_data = generate_binary(ir)
    write_binary_file(args.output_file, bin_data)

    if args.test:
        print_test_output(ir)