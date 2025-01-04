m = int(input(f'Enter number: '))
n = int(input(f'Enter number: '))
temp = []
with open('raw_text.txt', 'r') as file:
    for line in file:
        for i in range(len(line)):
            if (ord(line[i]) >= 97) and (ord(line[i]) <= 109) :
                unit = (m * n) % 26
                if (ord(line[i]) + unit) > 122 :
                    temp.append(chr(ord('a') + ord(line[i]) + unit - 123))
                else:
                    temp.append(chr(ord(line[i]) + unit))
            elif (ord(line[i]) >= 110) and (ord(line[i]) <= 122) :
                unit = (m + n) % 26
                if (ord(line[i]) - unit) < 97 :
                    temp.append(chr(ord('z') - ord(line[i]) - unit + 123))
                else:
                    temp.append(chr(ord(line[i]) - unit))
            elif (ord(line[i]) >= 65) and (ord(line[i]) <= 77) :
                unit = n % 26
                if (ord(line[i]) - unit) < 65 :
                    temp.append(chr(ord('Z') - ord(line[i]) - unit + 91))
                else:
                    temp.append(chr(ord(line[i]) - unit))
            elif (ord(line[i]) >= 78) and (ord(line[i]) <= 90) :
                unit = (m ** 2) % 26
                if (ord(line[i]) + unit) > 90 :
                    temp.append(chr(ord('A') + ord(line[i]) + unit - 91))
                else:
                    temp.append(chr(ord(line[i]) + unit))
            else:
                temp.append(line[i])

with open('encrypted_text.txt', 'w') as file:
    file.write(''.join(temp))

temp1 = []
with open('encrypted_text.txt', 'r') as file:
    for line in file:
        for i in range(len(line)):
            if (ord(line[i]) >= 97) and (ord(line[i]) <= 109) :
                unit = (m * n) % 26
                if (ord(line[i]) - unit) < 97 :
                    temp1.append(chr(ord('z') - ord(line[i]) - unit + 123))
                else:
                    temp1.append(chr(ord(line[i]) - unit))
            elif (ord(line[i]) >= 110) and (ord(line[i]) <= 122) :
                unit = (m + n) % 26
                if (ord(line[i]) + unit) > 122 :
                    temp1.append(chr(ord('a') + ord(line[i]) + unit - 123))
                else:
                    temp1.append(chr(ord(line[i]) - unit))
            elif (ord(line[i]) >= 65) and (ord(line[i]) <= 77) :
                unit = n % 26
                if (ord(line[i]) + unit) > 90 :
                    temp1.append(chr(ord('A') + ord(line[i]) + unit - 91))
                else:
                    temp1.append(chr(ord(line[i]) + unit))
            elif (ord(line[i]) >= 78) and (ord(line[i]) <= 90) :
                unit = (m ** 2) % 26
                if (ord(line[i]) - unit) < 65 :
                    temp1.append(chr(ord('Z') - ord(line[i]) - unit + 91))
                else:
                    temp1.append(chr(ord(line[i]) - unit))
            else:
                temp1.append(line[i])

with open('result.txt', 'w', encoding="utf-8") as file:
    file.write(''.join(temp1))
