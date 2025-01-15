import os

def encrypt_text(input_file, output_file, n, m):
    with open(input_file, 'r') as file:
        text = file.read()
    
    encrypted_text = ""
    label = []
    #Rule for label <value>: <meaning>
        # 0: unchanged
        # 1: first half lower case
        # 2: second half lower case
        # 3: first half upper case
        # 4: second half upper case
    for char in text:
        if 'a' <= char <= 'm':
            encrypted_text += chr((ord(char) - ord('a') + (n * m)) % 26 + ord('a'))
            label.append(1)
        elif 'n' <= char <= 'z':
            encrypted_text += chr((ord(char) - ord('a') - (n + m)) % 26 + ord('a'))
            label.append(2)
        elif 'A' <= char <= 'M':
            encrypted_text += chr((ord(char) - ord('A') - n) % 26 + ord('A'))
            label.append(3)
        elif 'N' <= char <= 'Z':
            encrypted_text += chr((ord(char) - ord('A') + (m**2)) % 26 + ord('A'))
            label.append(4)
        else:
            encrypted_text += char
            label.append(0)

    with open(output_file, 'w') as file:
        file.write(encrypted_text)

    return label

def decrypt_text(input_file, output_file, n, m, label):
    with open(input_file, 'r') as file:
        text = file.read()

    # Decryption
    decrypted_text = ""
    for i, char in enumerate(text):
        if label[i] == 1:
            first_half = chr((ord(char) - ord('a') - (n * m)) % 26 + ord('a'))
            decrypted_text += first_half
        elif label[i] == 2:
            second_half = chr((ord(char) - ord('a') + (n + m)) % 26 + ord('a'))
            decrypted_text += second_half
        elif label[i] == 3:
            first_half = chr((ord(char) - ord('A') + n) % 26 + ord('A'))
            decrypted_text += first_half
        elif label[i] == 4:
            second_half = chr((ord(char) - ord('A') - (m**2)) % 26 + ord('A'))
            decrypted_text += second_half
        else:
            decrypted_text += char
            
    with open(output_file, 'w') as file:
        file.write(decrypted_text)


def check_correctness(raw_file, decrypted_file):
    with open(raw_file, 'r') as file:
        raw_text = file.read()

    with open(decrypted_file, 'r') as file:
        decrypted_text = file.read()

    return raw_text == decrypted_text

script_dir = os.path.dirname(os.path.abspath(__file__))
raw_text = os.path.join(script_dir, "raw_text.txt")

encrypted_file = os.path.join(script_dir, "encrypted_text.txt")
decrypted_file = os.path.join(script_dir, "decrypted_text.txt")

n = int(input("Enter value for n: "))
m = int(input("Enter value for m: "))

label = ""
label = encrypt_text(raw_text, encrypted_file, n, m)

decrypt_text(encrypted_file, decrypted_file, n, m, label)
is_correct = check_correctness(raw_text, decrypted_file)

print("Decryption correctness:", is_correct)