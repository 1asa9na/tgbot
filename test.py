import requests
from time import sleep


class Ticker:
    def __init__(self, base, target, value, exchange):
        self.b = base
        self.t = target
        self.v = value
        self.e = exchange


class Cell:
    def __init__(self, ticker, coef):
        self.t = ticker
        self.c = coef

    def add(self, a):
        return Cell(self.t, self.c * a)


def std(brray):
    crray = [i.v for i in brray]
    return sum(crray) / len(crray)


def max_coefficient_cell(brray):
    result = brray[0]
    for i in brray:
        if i.c > result.c:
            result = i
    return result


exchanges = [i['id'] for i in requests.get("https://api.coingecko.com/api/v3/exchanges?per_page=50").json()]
print(exchanges)
array = {}
symbols = set()
for i in exchanges:
    sleep(2)
    print(f'\033[35m[{i.upper()}]\033[0m')
    response = requests.get(f'https://api.coingecko.com/api/v3/exchanges/{i}/tickers')
    if response.status_code != 200:
        print('\tTOO FAST')
    else:
        print('\tOK')
        tickers = response.json()['tickers']
        for j in tickers:
            if j["trust_score"] != "green" or j["is_anomaly"] != False:
                continue
            if (j['base'], j['target']) not in array:
                array[(j['target'], j['base'])] = [Ticker(j['target'], j['base'], j['last'], j['market']['name'])]
                array[(j['base'], j['target'])] = [Ticker(j['base'], j['target'], j['last'], j['market']['name'])]
            else:
                array[(j['base'], j['target'])].append(Ticker(j['base'], j['target'], j['last'], j['market']['name']))
                array[(j['target'], j['base'])].append(Ticker(j['target'], j['base'], j['last'], j['market']['name']))
                sorted(array[(j['base'], j['target'])], key=lambda x: x.v, reverse=True)
                symbols.add(j['base'])
                symbols.add(j['target'])
symbols = list(symbols)
for k in symbols:
    based_symb = k
    matrix = [[Cell(Ticker("NULL", "NULL", 0, "NONE"), 0) for i in range(len(symbols))] for j in range(len(symbols))]
    for i in range(len(symbols)):
        for j in range(i, len(symbols)):
            if (symbols[i], symbols[j]) in array:
                matrix[i][j] = Cell(max(array[(symbols[i], symbols[j])], key=lambda x: x.v),
                                    max(array[(symbols[i], symbols[j])], key=lambda x: x.v).v / std(
                                        array[(symbols[i], symbols[j])]))
    based_indx = symbols.index(based_symb)
    chain = []
    used_symbs = set()
    current_coef = 1
    while True:
        temp = [i.add(current_coef) for i in matrix[based_indx]]
        mx_coef = max_coefficient_cell(temp)
        if matrix[based_indx][temp.index(mx_coef)].c <= 1:
            break
        based_indx = temp.index(mx_coef)
        chain.append(mx_coef)
        current_coef = mx_coef.c
        if symbols[based_indx] in used_symbs:
            break
        else:
            used_symbs.add(symbols[based_indx])
    print("-"*len(k)+'\n'+k+'\n'+"-"*len(k))
    [print(f"{i.t.b}\t{i.t.t}\t{i.t.e}\t{i.t.v}\t{i.c}") for i in chain]
    print(str(current_coef)+'\n')