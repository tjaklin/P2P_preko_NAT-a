
def doMath():
    return 1+1

def findKey(key):
    if key in someDict:
        print('{} found!'.format(key))
    else:
        print('{} not found!'.format(key))

someDict = {
    'userA' : ['ip1', 'ip2']
}

myUser = 'userA'

if myUser in someDict:
    print('{}\'s private IP is {}. Public IP is {}'.format(myUser, someDict[myUser][0], someDict[myUser][1]))
else:
    print('No such user!')

findKey(myUser)

someVal = doMath()
print(someVal)
