import os

def encrypt_text(input_file, output_file, n, m):
    with open(input_file, 'r') as file:
        text = file.read()

    # Encryption
    encrypted_text = ""
    metadata = []
    for char in text:
        if 'a' <= char <= 'm':
            encrypted_text += chr((ord(char) - ord('a') + (n * m)) % 26 + ord('a'))
            metadata.append('first_half_lower')
        elif 'n' <= char <= 'z':
            encrypted_text += chr((ord(char) - ord('a') - (n + m)) % 26 + ord('a'))
            metadata.append('second_half_lower')
        elif 'A' <= char <= 'M':
            encrypted_text += chr((ord(char) - ord('A') - n) % 26 + ord('A'))
            metadata.append('first_half_upper')
        elif 'N' <= char <= 'Z':
            encrypted_text += chr((ord(char) - ord('A') + (m**2)) % 26 + ord('A'))
            metadata.append('second_half_upper')
        else:
            encrypted_text += char
            metadata.append('Unchanged')

    with open(output_file, 'w') as file:
        file.write(encrypted_text + '\n')
        file.write('\n')
        file.write(' '.join(metadata))

def decrypt_text(input_file, output_file, n, m):
    with open(input_file, 'r') as file:
        lines = file.readlines()
        text = lines[0].strip()
        metadata = lines[2].strip().split()

    # Decryption
    decrypted_text = ""
    for char, meta in zip(text, metadata):
        if meta == 'first_half_lower':
            first_half = chr((ord(char) - ord('a') - (n * m)) % 26 + ord('a'))
            decrypted_text += first_half
        elif meta == 'second_half_lower':
            second_half = chr((ord(char) - ord('a') + (n + m)) % 26 + ord('a'))
            decrypted_text += second_half
        elif meta == 'first_half_upper':
            first_half = chr((ord(char) - ord('A') + n) % 26 + ord('A'))
            decrypted_text += first_half
        elif meta == 'second_half_upper':
            second_half = chr((ord(char) - ord('A') - (m**2)) % 26 + ord('A'))
            decrypted_text += second_half
        else:
            decrypted_text += char
            
    with open(output_file, 'w') as file:
        file.write(decrypted_text)

def check_correctness(original_file, decrypted_file):
    with open(original_file, 'r') as file:
        original_text = file.read()

    with open(decrypted_file, 'r') as file:
        decrypted_text = file.read()

    return original_text == decrypted_text


script_dir = os.path.dirname(os.path.abspath(__file__))
raw_text = os.path.join(script_dir, "raw_text.txt")

encrypted_file = os.path.join(script_dir, "encrypted_text.txt")
decrypted_file = os.path.join(script_dir, "decrypted_text.txt")

n = int(input("Enter value for n: "))
m = int(input("Enter value for m: "))

metadata = encrypt_text(raw_text, encrypted_file, n, m)
decrypt_text(encrypted_file, decrypted_file, n, m)
is_correct = check_correctness(raw_text, decrypted_file)

print("Decryption correctness:", is_correct)

