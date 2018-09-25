import os, sys
from time import time

#def check_path(path):
#prod_struct = ['anim2dchar']
#2danim_struct = ['out', 'publish', 'work']

def init_struct(path):
	c = 0
	struct = {'2_prod':
					{'anim2dchar':
								{'out':'', 'publish':'', 'work':{'a':'boo'}}}}
	create_folder(path, struct)

def check_path(path):
	t0 = time()
	if os.path.exists(path):
		#print 'path %s exists' % path
		os.listdir(path)
	else:
		#print 'path %s doesnt exist' % path
		pass
	t1 = time()
	z = (t1-t0)
	if z > 0.1:
		print 'function check_path takes %f' %z
		print '----------------------------------------------------------', '\n'

def create_folder(path, struct):
	a = 1
	print struct
	try:
		TMP = struct.iteritems()
	except:
		TMP = None
	if TMP != None:
		print 'after while'
		raw_input("Press the <ENTER> key to continue...")
		for k, v in TMP:
			print 'start loop'
			struct_path = os.path.join(path, k)
			print 'SP', struct_path
			if not os.path.exists(struct_path):
				print 'MAKING DIR ---> %s' % struct_path
				#os.makedirs(struct_path)
			else:
				print 'folder %s exists' % struct_path
			print 'TRY GO DEEPER with:', v
			return create_folder(path, v) * a
			#try:
				#req_struct = v.iteritems()
				#print 'GO DEEP', v
				#return create_folder(path, v)
			#except:
				#print 'END', v
				##return create_folder(path, 'END')
				##return v 
				#pass
		#return create_folder(path, 'END')
	else:
		print 'EXIT'
		return 1
