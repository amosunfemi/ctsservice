
def double_preceding(values):
	retlist = []
	if len(values) == 0:
		pass
	else:
		for val in values:
			retlist.append(2*val)

	return retlist


list_val = [1,2,3,4,5,6]
print double_preceding(list_val)