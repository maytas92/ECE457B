class LinguisticLabel:
	# Linguistic label name could be 'verb', 'adjective', 'adverb', 'noun' etc
	# Membership functions is 
	def __init__(self, linguistic_label_name, *membership_functions):
		self._linguistic_label_name = linguistic_label_name
		self._membership_functions = membership_functions

def main():
	verb = LinguisticLabel('verb')

if __name__ == '__main__':
	main()