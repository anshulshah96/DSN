from Pos import *
import hashlib
import binascii
import random
import string

HASH_LENGTH = 32
RECORD_LENGTH = 36

def get_seed():
	rand = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
	return hashlib.sha256(rand).hexdigest()

def gen_challenge(seed, size):
	rand = seed
	p = Pos(seed, size)
	chal = p.gen_challenge().hashval
	chal = binascii.hexlify(chal)
	return (chal,p.path)

def verify(challenge, answer, solution):
	print(answer)
	print(solution)
	if answer==solution:
		return True
	return False

# print gen_challenge(96)
	