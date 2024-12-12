import sys
import json

def parse_instruction(line):
    # Пример формата строк:
    # LOAD_CONST 149, 511
    # LOAD_FROM_MEM 35, 456
    # STORE_TO_MEM 777, 882, 873
    # ROTR 444, 568, 561

    line = line.strip()
    if not line or line.startswith('#'):
        return None, None

    parts = line.split(None, 1)
    if len(parts) < 1:
        return None, None
    mnemonic = parts[0].upper()

    operands = []
    if len(parts) > 1:
        ops = parts[1]
        ops = ops.replace(" ", "")
        operands = ops.split(',')

    return mnemonic, [o.strip() for o in operands if o.strip()]

def assemble_instruction(mnemonic, operands):
    # В соответствии с заданием формируем двоичный код инструкции
    # Поля A, B, C, D - целочисленные, проверяем допустимые диапазоны по необходимости
    # Ниже - пример для 4 типов команд
    if mnemonic == 'LOAD_CONST':
        # A=11 (4 бита), B=21 бит, C=32 бит
        # Ожидаем 2 операнда: B, C
        # Формат бит (0 - младший бит):
        # биты 0–3: A
        # биты 4–24: B (21 бит)
        # биты 25–56: C (32 бит)
        # Размер: 8 байт (64 бита)
        A = 11
        if len(operands) != 2:
            raise ValueError("LOAD_CONST requires 2 operands")
        B = int(operands[0])
        C = int(operands[1])
        # Упаковываем биты
        instr_value = (A & 0xF)
        instr_value |= (B & ((1 << 21)-1)) << 4
        instr_value |= (C & ((1 << 32)-1)) << 25
        # Преобразуем в 8 байт
        instr_bytes = instr_value.to_bytes(8, byteorder='little', signed=False)
        return instr_bytes, {"opcode": A, "B": B, "C": C}

    elif mnemonic == 'LOAD_FROM_MEM':
        # A=0 (4 бита), B=32 бита, C=32 бита
        # Размер: 9 байт (72 бита)
        # Формат:
        # биты 0–3: A
        # биты 4–35: B (32 бит)
        # биты 36–67: C (32 бит)
        A = 0
        if len(operands) != 2:
            raise ValueError("LOAD_FROM_MEM requires 2 operands")
        B = int(operands[0])
        C = int(operands[1])
        instr_value = (A & 0xF)
        instr_value |= (B & ((1 << 32)-1)) << 4
        instr_value |= (C & ((1 << 32)-1)) << 36
        # 72 бита ~ 9 байт
        instr_bytes = instr_value.to_bytes(9, byteorder='little', signed=False)
        return instr_bytes, {"opcode": A, "B": B, "C": C}

    elif mnemonic == 'STORE_TO_MEM':
        # A=15 (4 бита), B=32 бита, C=32 бита, D=12 бит
        # Размер: 10 байт (80 бит)
        # Формат:
        # биты 0–3: A
        # биты 4–35: B
        # биты 36–67: C
        # биты 68–79: D
        A = 15
        if len(operands) != 3:
            raise ValueError("STORE_TO_MEM requires 3 operands (B, C, D)")
        B = int(operands[0])
        C = int(operands[1])
        D = int(operands[2])
        instr_value = (A & 0xF)
        instr_value |= (B & ((1 << 32)-1)) << 4
        instr_value |= (C & ((1 << 32)-1)) << 36
        instr_value |= (D & ((1 << 12)-1)) << 68
        instr_bytes = instr_value.to_bytes(10, byteorder='little', signed=False)
        return instr_bytes, {"opcode": A, "B": B, "C": C, "D": D}

    elif mnemonic == 'ROTR':
        # A=13 (4 бита), B=32 бита, C=32 бита, D=32 бита
        # Размер: 13 байт (104 бита)
        # Формат:
        # биты 0–3: A
        # биты 4–35: B
        # биты 36–67: C
        # биты 68–99: D
        A = 13
        if len(operands) != 3:
            raise ValueError("ROTR requires 3 operands (B, C, D)")
        B = int(operands[0])
        C = int(operands[1])
        D = int(operands[2])
        instr_value = (A & 0xF)
        instr_value |= (B & ((1 << 32)-1)) << 4
        instr_value |= (C & ((1 << 32)-1)) << 36
        instr_value |= (D & ((1 << 32)-1)) << 68
        instr_bytes = instr_value.to_bytes(13, byteorder='little', signed=False)
        return instr_bytes, {"opcode": A, "B": B, "C": C, "D": D}

    else:
        raise ValueError(f"Unknown instruction mnemonic: {mnemonic}")

def main():
    if len(sys.argv) < 4:
        print("Usage: python assembler.py <input_file> <output_file> <log_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    log_file = sys.argv[3]

    instructions_log = []

    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'wb') as f_out:
        for line in f_in:
            mnemonic, operands = parse_instruction(line)
            if mnemonic is None:
                continue
            instr_bytes, log_entry = assemble_instruction(mnemonic, operands)
            f_out.write(instr_bytes)
            # Добавим человекочитаемые операнды в лог
            log_entry["mnemonic"] = mnemonic
            log_entry["operands"] = operands
            instructions_log.append(log_entry)

    with open(log_file, 'w', encoding='utf-8') as f_log:
        json.dump(instructions_log, f_log, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()