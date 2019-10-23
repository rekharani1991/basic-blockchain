from DataSimulator import DataSimulator
import ECC
import math
import numpy as np

DSim = DataSimulator()

## difficulty of 4 zeroes given for nonce
difficulty = 4

## nodeDictionary stores all the valid nodes
nodeDictionary = []

# 'd' is the main Blockchain in which objects of class Block is added as asked for in HW
d = []

# this is the message that is to be searched
Msg="cabinet meets to balance budget priorities"
#Msg="baby badly burnt in brisbane house fire"

class my_dictionary(dict):
    # __init__ function
    def __init__(self):
        self = dict()
    
    # Function to add key:value
    def add(self, key, value):
        self[key] = value

# global_dictionary stores all the tuples of all the data read from JSON file.
global_dictionary = my_dictionary()

# Struture of Block which will be part of Blockchain
class Block:
    def __init__(self, previous_hash, root, nonce):
        self.root = root
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.blockHash = None


'''
    getVerfiedTuples() gives all the valid tuples read from JSON file for each block
'''
def getVerifiedTuples():
    counter = 0
    counterT = 0
    counterV = 0
    verifiedTuples = []
    d = DSim.getNewData()  # A set of tuples is returned
    for p in d:
        thistuple = (p['pk'], p['msg'], p['signature'])
        isVerified = ECC.verify(thistuple[0], thistuple[1], thistuple[2])
        global_dictionary.key = thistuple[1]
        global_dictionary.value = thistuple
        global_dictionary.add(global_dictionary.key, global_dictionary.value)

        if (isVerified):
            verifiedTuples.append(thistuple)
    
    return verifiedTuples

# hashNonce function is used to calculate nonce value which statifies the given diffculty level for hash of block
def hashNonce(newBlock):
    newBlock.blockHash = ECC.hash(str(newBlock))
    while not newBlock.blockHash.startswith('0' * difficulty):
        newBlock.nonce += 1
        newBlock.blockHash = ECC.hash(str(newBlock.previous_hash) + str(newBlock.root) + str(newBlock.nonce))
    return newBlock.blockHash, newBlock.nonce

# This function builds the Merkel Tree by taking a set of all valid tuples, start index of node, last index of node
# and returns the hash of root node
def buildMerkleTree(listOfElement, posLeft, posRight):
    # if we are at a leaf
    if (posLeft == posRight):
        return ECC.hash(str(listOfElement[posLeft]))
    

    centerElement = (posLeft+posRight)/2
    leftHash = buildMerkleTree(listOfElement, posLeft, centerElement)
    rightHash = buildMerkleTree(listOfElement, centerElement+1, posRight)
    temp = [leftHash,rightHash]
    nodeDictionary.append(temp)
    return ECC.hash(str(rightHash+leftHash))

# This function finds the adjacent node of current child
def findNeighbour(node,nodeDictionary):
    result=(np.where(nodeDictionary == node))
    if(len(result) != 0):
        listOfCoordinates= list(zip(result[0], result[1]))
    
        return listOfCoordinates
    else :
        return None

##################################################################
# Main Function

''' STEP 1 : Create Merkel Tree
    Get Verified Tuples for each block
    Add Block in blockchain 'd': previousHash, Merkel Root Node, Nonce and Self Hash
'''
for i in range(0, 6):
    # create Merkel Tree of this fetched verified data
    VT=getVerifiedTuples()
    charuBinary=buildMerkleTree(VT,0,len(VT)-1)
    #charuBinary=buildMerkleTree(getVerifiedTuples()[0:6],0,5)
    nodeDictionary.append([charuBinary,0])
    
    # create a valid block
    if i != 0:
        t = Block((str(d[i - 1].blockHash)), charuBinary, 0)
        t.blockHash, t.nonce = hashNonce(t)
    else:
        t = Block(0, charuBinary, 0)
        t.blockHash, t.nonce = hashNonce(t)
    
    # add the new block in blockchain with DataStructure d
    d.append(t)

print '\n','Block Chains :'
for b in d:
    print'\n', '| Self Hash:', b.blockHash, '| Prev Hash:', b.previous_hash, '| MT:', b.root, "| Nonce:", b.nonce

''' STEP 2 : Search for Message to be verfied in global dictionary and find its hash value using pk,sig,msg.
'''
msgtuple = global_dictionary.get(Msg,"No Entry Found")
print '\n','Given Msg : ',Msg
print 'Msg Tuple[pk,msg,sig]',msgtuple

''' To Print all items in nodeDictionary
for n in nodeDictionary :
    print(n)
'''

nodeDictionary = np.array(nodeDictionary)

'''
      Step 3 Verify the Entered Message
 This part calculates the H(Z) = H(current node) + H(neighbouring node) using recursive calls
 First it verifies if that Message is Valid or not usig ECC.verify function
 it then takes the hash value of the message , search for that node's indices for that msg in nodeDictinary
 and depending on whether it is left or right node, added hash is calculated: Right H(S)+H(N)  or h(N)+h(S) is done.
 Now, this calculated hash is used further to build the path of merkel tree using only given message.
'''

addHash=None
if ECC.verify(msgtuple[0], msgtuple[1], msgtuple[2]):
    selfHash = ECC.hash(str(msgtuple))
    addHash=selfHash
    print 'Hash(Given Message) :',selfHash,'\n'

    while True:
        lc=findNeighbour(addHash,nodeDictionary)
        if len(lc) !=0 :
            neighbour=nodeDictionary[lc[0][0]][abs(lc[0][1]-1)]
            selfHash=addHash
            if (neighbour !='0'):
                if abs(lc[0][1]) == 1 :
                    addHash = ECC.hash(str(selfHash) + str(neighbour))
                else :
                    addHash = ECC.hash(str(neighbour) + str(selfHash))
                print 'Calculated Hash of upper node',addHash,' = h(Neighbour =' , neighbour, ') + h(Self =', selfHash, ')'

            # if a valid addhash value is returned then, it is a part of Merkel Tree with root hash=final addhash
            else :
                print '\n','Final calculated Hash =',addHash
                print 'Given message is a part of Merkle Tree.'
                break
        else :
            print('No Valid Merkel Tree can be creted')
            break

## This part compares the calculated has with merkel tree hashes given in Blockchain, if it matches then this message is part of the given blockchain
i=0
for b in d :
    i +=1
    if b.root==addHash :
        print '\n\n','Message is found in the Merkel Tree of Block : ',i,' -->',(b.previous_hash,b.root,b.nonce,b.blockHash)
        break
if i > len(d):
    print('Given Message is not part of BlockChain')

# printing of blocks
