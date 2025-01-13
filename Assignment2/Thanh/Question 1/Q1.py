
def encrypted_text(m, n):
    temp = []
    label = []

    with open('raw_text.txt', 'r') as file:
        for line in file:
            for i in range(len(line)):
                if (ord(line[i]) >= 97) and (ord(line[i]) <= 109) :
                    unit = (m * n) % 26
                    if (ord(line[i]) + unit) > 122 :
                        temp.append(chr(ord('a') + ord(line[i]) + unit - 123))
                    else:
                        temp.append(chr(ord(line[i]) + unit))
                    label.append(1)
                elif (ord(line[i]) >= 110) and (ord(line[i]) <= 122) :
                    unit = (m + n) % 26
                    if (ord(line[i]) - unit) < 97 :
                        temp.append(chr(ord('z') - ord(line[i]) - unit + 123))
                    else:
                        temp.append(chr(ord(line[i]) - unit))
                    label.append(2)
                elif (ord(line[i]) >= 65) and (ord(line[i]) <= 77) :
                    unit = n % 26
                    if (ord(line[i]) - unit) < 65 :
                        temp.append(chr(ord('Z') - ord(line[i]) - unit + 91))
                    else:
                        temp.append(chr(ord(line[i]) - unit))
                    label.append(3)
                elif (ord(line[i]) >= 78) and (ord(line[i]) <= 90) :
                    unit = (m ** 2) % 26
                    if (ord(line[i]) + unit) > 90 :
                        temp.append(chr(ord('A') + ord(line[i]) + unit - 91))
                    else:
                        temp.append(chr(ord(line[i]) + unit))
                    label.append(4)
                else:
                    temp.append(line[i])
                    label.append(0)

    with open('encrypted_text.txt', 'w') as file:
        file.write(''.join(temp))
    return label

def decrypted_text(m, n, label):
    temp1 = []
    with open('encrypted_text.txt', 'r') as file:
        for line in file:
            for i in range(len(line)):
                if label[i] == 1 :
                    unit = (m * n) % 26
                    if (ord(line[i]) - unit) < 97 :
                        temp1.append(chr(ord('z') - unit + ord(line[i]) - ord('a') + 1))
                    else:
                        temp1.append(chr(ord(line[i]) - unit))
                elif label[i] == 2 :
                    unit = (m + n) % 26
                    if (ord(line[i]) + unit) > 122 :
                        temp1.append(chr(ord('a') + unit - ord('z') + ord(line[i]) - 1))
                    else:
                        temp1.append(chr(ord(line[i]) + unit))
                elif label[i] == 3 :
                    unit = n % 26
                    if (ord(line[i]) + unit) > 90 :
                        temp1.append(chr(ord('A') + unit - ord('Z') + ord(line[i]) - 1))
                    else:
                        temp1.append(chr(ord(line[i]) + unit))
                elif label[i] == 4 :
                    unit = (m ** 2) % 26
                    if (ord(line[i]) - unit) < 65 :
                        temp1.append(chr(ord('Z') - unit + ord(line[i]) - ord('A') + 1))
                    else:
                        temp1.append(chr(ord(line[i]) - unit))
                else:
                    temp1.append(line[i])

    with open('decrypted_text.txt', 'w', encoding="utf-8") as file:
        file.write(''.join(temp1))

def check_correctness(raw_text, decrypted_text):
    return raw_text == decrypted_text

m = int(input(f'Enter number for m: '))
n = int(input(f'Enter number for n: '))

label = []
raw = []
decrypted = []
label = encrypted_text(m, n)

decrypted_text(m, n, label)

with open('raw_text.txt', 'r') as file:
    for line in file:
        raw = line

with open('decrypted_text.txt', 'r') as file:
    for line in file:
        decrypted = line

if check_correctness(raw, decrypted):
    print("Decryption successful. The decrypted text matches the original.")
else:
    print("Decryption failed. The decrypted text does not match the original.")