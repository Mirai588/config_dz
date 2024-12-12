import unittest
import subprocess
import os

class TestInstructionBytes(unittest.TestCase):
    def setUp(self):
        self.assembler = 'python assembler.py'  # или 'python3', если необходимо
        self.temp_asm = 'temp_test.asm'
        self.temp_bin = 'temp_test.bin'
        self.temp_log = 'temp_test_log.json'

    def tearDown(self):
        for f in [self.temp_asm, self.temp_bin, self.temp_log]:
            if os.path.exists(f):
                os.remove(f)

    def run_assembler(self, asm_code: str):
        # Записываем asm код во временный файл
        with open(self.temp_asm, 'w', encoding='utf-8') as f:
            f.write(asm_code)
        # Запускаем ассемблер
        cmd = f"{self.assembler} {self.temp_asm} {self.temp_bin} {self.temp_log}"
        result = subprocess.run(cmd, shell=True, capture_output=True)
        self.assertEqual(result.returncode, 0, msg=f"Assembler failed: {result.stderr.decode('utf-8')}")
        # Читаем результат
        with open(self.temp_bin, 'rb') as f:
            return f.read()

    def test_load_const(self):
        # Тест из условия:
        # A=11,B=149,C=511
        # Ожидаемый результат:
        # 0x5B, 0x09, 0x00, 0xFE, 0x03, 0x00, 0x00, 0x00
        expected_bytes = bytes([0x5B, 0x09, 0x00, 0xFE, 0x03, 0x00, 0x00, 0x00])
        # Аналог команды: LOAD_CONST 149,511
        asm_code = "LOAD_CONST 149, 511\n"
        actual = self.run_assembler(asm_code)
        self.assertEqual(actual, expected_bytes)

    def test_load_from_mem(self):
        # Тест из условия:
        # A=0,B=35,C=456
        # Ожидаемый результат:
        # 0x30, 0x02, 0x00, 0x00, 0x80, 0x1C, 0x00, 0x00, 0x00
        expected_bytes = bytes([0x30,0x02,0x00,0x00,0x80,0x1C,0x00,0x00,0x00])
        # Аналог команды: LOAD_FROM_MEM 35,456
        asm_code = "LOAD_FROM_MEM 35, 456\n"
        actual = self.run_assembler(asm_code)
        self.assertEqual(actual, expected_bytes)

    def test_store_to_mem(self):
        # Тест из условия:
        # A=15,B=777,C=882,D=873
        # Ожидаемые байты:
        # 0x9F, 0x30, 0x00, 0x00, 0x20, 0x37, 0x00, 0x00, 0x90, 0x36
        expected_bytes = bytes([0x9F,0x30,0x00,0x00,0x20,0x37,0x00,0x00,0x90,0x36])
        # Аналог команды: STORE_TO_MEM 777,882,873
        asm_code = "STORE_TO_MEM 777, 882, 873\n"
        actual = self.run_assembler(asm_code)
        self.assertEqual(actual, expected_bytes)

    def test_rotr(self):
        # Тест из условия:
        # A=13,B=444,C=568,D=561
        # Ожидаемые байты:
        # 0xCD, 0x1B, 0x00, 0x00, 0x80, 0x23, 0x00, 0x00, 0x10, 0x23, 0x00, 0x00, 0x00
        expected_bytes = bytes([0xCD,0x1B,0x00,0x00,0x80,0x23,0x00,0x00,0x10,0x23,0x00,0x00,0x00])
        # Аналог команды: ROTR 444,568,561
        asm_code = "ROTR 444, 568, 561\n"
        actual = self.run_assembler(asm_code)
        self.assertEqual(actual, expected_bytes)


if __name__ == '__main__':
    unittest.main()