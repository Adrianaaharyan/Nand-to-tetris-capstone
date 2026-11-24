import sys
from pathlib import Path

# Predefined Hack symbols
SYMBOLS = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576
}

for i in range(16):
    SYMBOLS[f"R{i}"] = i

# Hack computation instructions
COMP = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "M": "1110000",
    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",
    "-D": "0001111",
    "-A": "0110011",
    "-M": "1110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "D+M": "1000010",
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "D&M": "1000000",
    "D|A": "0010101",
    "D|M": "1010101"
}

# Destination bits
DEST = {
    "": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
}

# Jump bits
JUMP = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}


def clean_lines(filename):
    """Remove comments, blank lines and unnecessary spaces."""
    instructions = []

    with open(filename, "r") as file:
        for line_number, line in enumerate(file, 1):
            line = line.split("//")[0]
            line = line.strip().replace(" ", "").replace("\t", "")

            if line:
                instructions.append((line_number, line))

    return instructions


def first_pass(instructions):
    """Identify labels and warn about duplicate labels."""
    symbols = SYMBOLS.copy()
    rom_address = 0
    seen_labels = set()

    for line_number, instruction in instructions:

        if instruction.startswith("(") and instruction.endswith(")"):
            label = instruction[1:-1]

            if not label:
                raise ValueError(
                    f"Line {line_number}: empty label"
                )

            if label in seen_labels or label in SYMBOLS:
                print(
                    f"Warning: Line {line_number}: "
                    f"duplicate label '{label}'"
                )
            else:
                symbols[label] = rom_address
                seen_labels.add(label)

        else:
            rom_address += 1

    return symbols


def assemble_a(instruction, symbols, next_variable):
    """Translate A-instructions into 16-bit binary."""
    symbol = instruction[1:]

    if not symbol:
        raise ValueError("empty A-instruction")

    if symbol.isdigit():
        address = int(symbol)

    else:
        if symbol not in symbols:
            symbols[symbol] = next_variable[0]
            next_variable[0] += 1

        address = symbols[symbol]

    if not 0 <= address <= 32767:
        raise ValueError("A-instruction address out of range")

    return format(address, "016b")


def assemble_c(instruction):
    """Translate C-instructions into 16-bit binary."""

    if instruction.count("=") > 1 or instruction.count(";") > 1:
        raise ValueError("invalid C-instruction")

    if "=" in instruction:
        dest, remaining = instruction.split("=", 1)
    else:
        dest, remaining = "", instruction

    if ";" in remaining:
        comp, jump = remaining.split(";", 1)
    else:
        comp, jump = remaining, ""

    # Validate and normalize destination registers
    if dest:
        if (
            any(ch not in "ADM" for ch in dest)
            or len(set(dest)) != len(dest)
        ):
            raise ValueError(f"invalid destination: {dest}")

        dest = "".join(ch for ch in "AMD" if ch in dest)

    if dest not in DEST:
        raise ValueError(f"invalid destination: {dest}")

    if comp not in COMP:
        raise ValueError(f"invalid computation: {comp}")

    if jump not in JUMP:
        raise ValueError(f"invalid jump: {jump}")

    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def assemble(input_file, output_file):
    """Perform two-pass assembly and generate machine code."""

    instructions = clean_lines(input_file)

    # PASS 1: Identify labels and duplicate-label warnings
    symbols = first_pass(instructions)

    # PASS 2: Generate machine code
    machine_code = []
    next_variable = [16]

    for line_number, instruction in instructions:

        if instruction.startswith("(") and instruction.endswith(")"):
            continue

        try:
            if instruction.startswith("@"):
                binary = assemble_a(
                    instruction,
                    symbols,
                    next_variable
                )
            else:
                binary = assemble_c(instruction)

            machine_code.append(binary)

        except ValueError as error:
            raise ValueError(
                f"Line {line_number}: {error}"
            ) from error

    with open(output_file, "w") as file:
        file.write("\n".join(machine_code) + "\n")

    print("\nAssembly successful!")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"Instructions generated: {len(machine_code)}")


if __name__ == "__main__":

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python assembler.py input.asm [output.hack]")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.is_file():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    output_path = (
        Path(sys.argv[2])
        if len(sys.argv) == 3
        else input_path.with_suffix(".hack")
    )

    try:
        assemble(input_path, output_path)

    except (ValueError, OSError) as error:
        print(f"Error: {error}")
        sys.exit(1)
