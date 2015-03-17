_DEBUG = 0

class TextReader:
	def __init__(self, file_name):
		self._file_name = file_name

	def open(self):
		self._file_object = open(self._file_name, 'r')

	def close(self):
		self._file_object.close()

	def read(self):
		for line in self._file_object:
			yield line

class ValenceData:
	def __init__(self, file_name):
		self._tr = TextReader(file_name)
		self._tr.open()
		self._data_map = {}

	def process_data(self):
		for line in self._tr.read():
			[word, valence_score] = line.split('\t')
			self._data_map[word] = valence_score

if __name__ == '__main__':
	valence_data = ValenceData('../data/valence.txt')
	valence_data.process_data()

	for k, v in valence_data._data_map.items():
		print k, v
