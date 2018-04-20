import random
import hashlib
import os
import binascii

HASH_LENGTH = 32
RECORD_LENGTH = 36

class Challenge(object):
    """The challenge object that represents a challenge posed to the server
    for proof of space    """

    def __init__(self, hashval):
        """Initialization method

        :param hashval : value of the hash to be founded
        """
        self.hashval = hashval

    def todict(self):
        """Returns a dictionary fully representing the state of this object
        """
        return {"hashval": self.hashval}

    @staticmethod
    def fromdict(dict):
        """Takes a dictionary as an argument and returns a new Challenge
        object from the dictionary.
        """
        pass

    def get_hashval(self):
        return self.hashval

class Proof(object):
    """This class encapsulates proof of space returned by the provider
    """

    def __init__(self,path):
        """Initialization method"""
        self.path = path

    def todict(self):
        """Returns a dictionary fully representing the state of this object
        """
        return {"path" : self.path}

    @staticmethod
    def fromdict(dict):
        """Takes a dictionary as an argument and returns a new Proof object
        from the dictionary.

        """
        pass

    def getPath(self):
        return self.path

class Pos(object):
    def __init__(self, seed, filesz, path=None):
        """Initialization method

        :param seed: the root of the merkle tree
        :param filesz: the size of the file
        :param path: path of the challenge on merkle tree

        """
        self.seed = seed
        self.filesz = filesz
        self.path = path
        # self.challenges = list()
        # self.verifs = list()

    def todict(self):
        return {"seed": self.seed,
                "filesz": self.filesz,
                "path": self.path}

    @staticmethod
    def fromdict(dict):
        pass

    def gen_challenge(self):
        path = random.randint(1,self.filesz/HASH_LENGTH)
        self.path = path
        strpath = ""
        while path>1:
            if path%2==0:
                strpath+='0'
            else:
                strpath+='1'
            path/=2
            path=int(path)
        strpath = strpath[::-1] 
        i=0
        curr = self.seed
        curr = bytearray.fromhex(curr)
        curr = bytes(curr)
        while i<len(strpath):
            if(strpath[i]=='0'):
                curr=bytearray.fromhex(hashlib.sha256((str(curr)+'0').encode('utf-8')).hexdigest())
            else:
                curr=bytearray.fromhex(hashlib.sha256((str(curr)+'1').encode('utf-8')).hexdigest())
            i+=1
            curr = bytes(curr)
        return Challenge(curr)

    def verify(self, proof):
        if proof.path == self.path:
            return true
        else:
            return false


class Pos_provider(object):
    def __init__(self, seed, filesz, file):
        """Initialization method

        :param seed: the root of the merkle tree
        :param filesz: the size of the file
        :param file: file used to read and write

        """
        self.seed = seed
        self.filesz = filesz
        self.exacfilesz = filesz
        self.file = file
        # self.challenges = list()
        # self.verifs = list()

    def todict(self):
        return {"seed": self.seed,
                "filesz": self.filesz,
                "file": self.file}

    @staticmethod
    def fromdict(dict):
        pass

    def setup(self):
        open(self.file, 'wb').close()
        file = open(self.file,'rb+')

        temp = self.seed + hex(1)[2:].zfill(8)
        file.write(bytearray.fromhex(temp))
        i=2
        while i<=self.filesz/HASH_LENGTH:
            file.seek((int)(i/2-1)*RECORD_LENGTH)
            par = file.read(HASH_LENGTH)
            temp = hashlib.sha256((str(par)+'0').encode('utf-8')).hexdigest() + hex(i)[2:].zfill(8)
            file.seek(0,2)
            file.write(bytearray.fromhex(temp))
            i+=1
            if i<=self.filesz/HASH_LENGTH:
                temp = hashlib.sha256((str(par)+'1').encode('utf-8')).hexdigest() + hex(i)[2:].zfill(8)
                file.seek(0,2)
                file.write(bytearray.fromhex(temp))
                i+=1

        self.exacfilesz = (i-1)*RECORD_LENGTH
        file.close()
        os.system("export PATH=$PATH:~/go/bin"  )
        os.system("binsort -s 36 ./"+ self.file + " ./" + self.file)

    def prove(self,challenge):
        file = open(self.file,'rb')

        h = challenge.hashval

        left = 0
        right = self.exacfilesz/RECORD_LENGTH-1
        curr = None
        path = None

        while curr!=h and left<=right:
            mid = (left+right)/2
            mid = int(mid)
            file.seek(int(mid)*RECORD_LENGTH)
            curr = file.read(HASH_LENGTH)
            
            if curr==h:
                path = file.read(4)
                break
            elif curr>h:
                right=mid-1
            else:
                left=mid+1

        if path!=None:
            return int(binascii.hexlify(path),16)
            
# HASH_LENGTH = 32
# RECORD_LENGTH = 36
# p = Pos(hashlib.sha256('0').hexdigest(), 320000000)
# q = Pos_provider(hashlib.sha256('0').hexdigest(), 320000000, 'testing')
# q.setup()
# chal = p.gen_challenge()
# print "Initial Path " , p.path
# print "Hash ", binascii.hexlify(chal.hashval)
# path = q.prove(chal)
# print "Path " , path