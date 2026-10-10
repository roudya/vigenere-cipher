import json


def vigenere(text, key, decrypt=False):
    result = ""
    key_index = 0
    key = key.upper()

    for char in text:
        if "A" <= char <= "Z" or "a" <= char <= "z":
            base = ord("A") if char.isupper() else ord("a")
            shift = ord(key[key_index % len(key)]) - ord("A")
            if decrypt:
                shift = -shift
            result += chr((ord(char) - base + shift) % 26 + base)
            key_index += 1
        else:
            result += char

    return result


def read_order(prompt):
    order = [int(number) - 1 for number in input(prompt).split()]
    if not order or sorted(order) != list(range(len(order))):
        raise ValueError("An order must contain each number from 1 to its size once.")
    return order


def inverse_order(order):
    inverse = [0] * len(order)
    for position, value in enumerate(order):
        inverse[value] = position
    return inverse


def permute(text, row_order, column_order, kind, decrypt=False):
    rows = len(row_order)
    columns = len(column_order)
    block_size = rows * columns
    order = row_order if kind == "r" else column_order
    if decrypt:
        order = inverse_order(order)
    result = ""

    for start in range(0, len(text), block_size):
        block = text[start:start + block_size]
        grid = [list(block[i:i + columns]) for i in range(0, block_size, columns)]
        if kind == "r":
            grid = [grid[i] for i in order]
        else:
            grid = [[row[i] for i in order] for row in grid]
        result += "".join("".join(row) for row in grid)

    return result


def encrypt(text, key, row_order, column_order, rounds):
    length = len(text)
    text = vigenere(text, key)
    print("After Vigenere:", text)
    if rounds:
        block_size = len(row_order) * len(column_order)
        text += "X" * ((-len(text)) % block_size)

    for number, kind in enumerate(rounds, 1):
        text = permute(text, row_order, column_order, kind)
        name = "rows" if kind == "r" else "columns"
        print(f"Round {number} ({name}): {text}")

    return json.dumps([length, text], ensure_ascii=False)


def decrypt(ciphertext, key, row_order, column_order, rounds):
    data = json.loads(ciphertext)
    if not isinstance(data, list) or len(data) != 2:
        raise ValueError("Copy the complete ciphertext, including the brackets.")
    length, text = data
    if type(length) is not int or length < 0 or not isinstance(text, str):
        raise ValueError("Invalid ciphertext format.")
    block_size = len(row_order) * len(column_order)
    expected_size = ((length + block_size - 1) // block_size) * block_size
    if len(text) != (expected_size if rounds else length):
        raise ValueError("The ciphertext length does not match these settings.")

    for number in range(len(rounds) - 1, -1, -1):
        kind = rounds[number]
        text = permute(text, row_order, column_order, kind, True)
        name = "rows" if kind == "r" else "columns"
        print(f"Undo round {number + 1} ({name}): {text}")

    return vigenere(text[:length], key, True)


def main():
    print("Vigenere Cipher")
    print("1. Encrypt")
    print("2. Decrypt")

    try:
        mode = input("Choose 1 or 2: ").strip()
        if mode not in ("1", "2"):
            raise ValueError("Choose 1 for encryption or 2 for decryption.")
        text = input("Plaintext: " if mode == "1" else "Ciphertext: ")
        key = input("Secret key: ").strip()
        if not key or any(not ("A" <= c <= "Z" or "a" <= c <= "z") for c in key):
            raise ValueError("The secret key must contain only English letters.")
        row_order = read_order("Row order (e.g. 2 1): ")
        column_order = read_order("Column order (e.g. 3 1 2): ")
        rounds = input("Rounds (e.g. c r c; Enter for none): ").lower().split()
        if any(kind not in ("r", "c") for kind in rounds):
            raise ValueError("Use r for a row round and c for a column round.")
        print()

        if mode == "1":
            result = encrypt(text, key, row_order, column_order, rounds)
            print("Ciphertext:")
        else:
            result = decrypt(text, key, row_order, column_order, rounds)
            print("Plaintext:")
        print(result)
    except ValueError as error:
        print("Error:", error)


if __name__ == "__main__":
    main()
