import random
library = ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", ]
vocals = ["a", "e", "i", "o", "u",]
name = []
def generate():
    length = random.randint(3,6)
    for i in range(0,length):
        addvoc = random.randint(1, 300)
        add = addvoc % 2
        if add == 0:
            addv = random.randint(0,4)
            name.append(vocals[addv])
        elif add != 0:
            let = random.randint(0,21)
            name.append(library[let])
        res = ''.join(str(n) for n in name)
    del name[:]
    return res
