import re

def find_home(string, home_number):
    mas = string.split(sep=',')
    for i in mas:
        if i.strip() == str(home_number):
            return True
        result = re.search(r'\d+-\d+', i.strip())
        if result:
            first = (re.search(r'^\d+', result.group(0))).group(0)
            second = (re.search(r'\d+$', result.group(0))).group(0)
            #print(first)
            #print(second)
            if ((int(first) < int(home_number)) and (int(second) > int(home_number))):
                return True
    return False

print(find_home('vdbvzdcf 11, 12, 44, 10-15, dsfvfsd', 13))
print(find_home('dfg 11, dsfgdfg, 12, 44, 10-15', 11))
print(find_home('11, dsfgfd-dsfg, 12, 44, 10-15', 12))
print(find_home('11, 12ad-34sdfg, 12, 44, 10-15', 16))
