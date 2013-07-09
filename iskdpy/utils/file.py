
def read(file):
	try:
		output = open(file , 'rb')
		tmp=output.read()
		output.close()
	except IOError:
		return ""
	else:
		return tmp

def write(file, data):
	try:
		output = open(file , 'wb')
		output.write(data)
		output.close()
	except IOError:
		return False
	else:
		return True

