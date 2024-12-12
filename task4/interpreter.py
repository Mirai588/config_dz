import sys
import json

def rotate_right(value, shift, bits=32):
    shift = shift % bits
    return ((value >> shift) | (value << (bits - shift))) & ((1 << bits) - 1)

def main():
    if len(sys.argv) < 6:
        print("Usage: python interpreter.py <binary_file> <result_file> <mem_start> <mem_end> <mem_dump_json>")
        sys.exit(1)

    binary_file = sys.argv[1]
    result_file = sys.argv[2]
    mem_start = int(sys.argv[3])
    mem_end = int(sys.argv[4])
    mem_dump_json = sys.argv[5]

    memory = {}  # простая модель памяти

    with open(binary_file, 'rb') as f:
        code = f.read()

    pc = 0
    code_len = len(code)

    while pc < code_len:
        # Читаем 1 байт, чтобы определить A (4 бита)
        if pc >= code_len:
            break
        first_byte = code[pc]
        A = first_byte & 0xF

        if A == 11:
            # LOAD_CONST (8 байт)
            # A=11, B=21 бит, C=32 бита
            # Уже считан первый байт, нужно считать всего 8 байт
            if pc+8 > code_len:
                print("Error: Truncated LOAD_CONST")
                break
            instr = int.from_bytes(code[pc:pc+8], 'little', signed=False)
            pc += 8

            # Парсим поля
            A = instr & 0xF
            B = (instr >> 4) & ((1 << 21)-1)
            C = (instr >> 25) & ((1 << 32)-1)

            # Записываем B в память[C]
            memory[C] = B

        elif A == 0:
            # LOAD_FROM_MEM (9 байт)
            if pc+9 > code_len:
                print("Error: Truncated LOAD_FROM_MEM")
                break
            instr = int.from_bytes(code[pc:pc+9], 'little', signed=False)
            pc += 9

            A = instr & 0xF
            B = (instr >> 4) & ((1 << 32)-1)
            C = (instr >> 36) & ((1 << 32)-1)

            # В memory[B] запишем значение memory[memory[C]]
            addr_c = memory.get(C, 0)
            val = memory.get(addr_c, 0)
            memory[B] = val

        elif A == 15:
            # STORE_TO_MEM (10 байт)
            if pc+10 > code_len:
                print("Error: Truncated STORE_TO_MEM")
                break
            instr = int.from_bytes(code[pc:pc+10], 'little', signed=False)
            pc += 10

            A = instr & 0xF
            B = (instr >> 4) & ((1 << 32)-1)
            C = (instr >> 36) & ((1 << 32)-1)
            D = (instr >> 68) & ((1 << 12)-1)

            # memory[memory[C] + D] = memory[B]
            base = memory.get(C, 0)
            val = memory.get(B, 0)
            memory[base + D] = val

        elif A == 13:
            # ROTR (13 байт)
            if pc+13 > code_len:
                print("Error: Truncated ROTR")
                break
            instr = int.from_bytes(code[pc:pc+13], 'little', signed=False)
            pc += 13

            A = instr & 0xF
            B = (instr >> 4) & ((1 << 32)-1)
            C = (instr >> 36) & ((1 << 32)-1)
            D = (instr >> 68) & ((1 << 32)-1)

            # Операнды: valueC = memory[memory[C]], shift = memory[memory[B]]
            # Результат: memory[memory[D]] = rotate_right(valueC, shift)
            addr_c = memory.get(C, 0)
            addr_b = memory.get(B, 0)
            addr_d = memory.get(D, 0)

            value_c = memory.get(addr_c, 0)
            shift = memory.get(addr_b, 0)
            rotated = rotate_right(value_c, shift, 32)
            memory[addr_d] = rotated

        else:
            print(f"Unknown opcode A={A} at PC={pc}")
            break

    # Выгружаем диапазон памяти [mem_start, mem_end] в result_file (json)
    result = {}
    for addr in range(mem_start, mem_end+1):
        result[addr] = memory.get(addr, 0)

    with open(result_file, 'w', encoding='utf-8') as f_out:
        json.dump(result, f_out, ensure_ascii=False, indent=2)

    # Также сохраним всю память в отдельный json (например, для отладки)
    with open(mem_dump_json, 'w', encoding='utf-8') as f_dump:
        mem_all = {str(k): v for k, v in memory.items()}
        json.dump(mem_all, f_dump, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()