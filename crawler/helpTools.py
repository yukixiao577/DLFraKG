with open("noJson.txt", "r", encoding="utf-8") as f:
    li = f.read()
    temp = []
    for i in li.split(']'):
        if i == '':
            continue
        if i.startswith(','):
            i = i[1:]
        temp.append(i + ']')
with open("noJson.txt", "w", encoding="utf-8") as f:
    for i in temp:
        f.write(i + '\n')
