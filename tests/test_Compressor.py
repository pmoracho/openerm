import unittest

from openerm.Compressor import Compressor

class CompressorTest(unittest.TestCase):

	def test_compressor_with_random_data(self):
		"""Verificar todos los algoritmos de compresión con información random
		"""
		import string
		import random

		def rnd_generator(size=1024, chars=string.ascii_uppercase + string.digits):
			return ''.join(random.choice(chars) for _ in range(size))

		random_text = rnd_generator(size=200).encode("utf-8")

		c = Compressor()
		for t in c.available_types:
			with self.subTest(i=t[0]):
				c.type = t[0]
				c.level = 1
				tmp = c.compress(random_text)
				tmp = c.decompress(tmp)
				self.assertEqual(random_text, tmp)

	def test_compressor_with_text_data(self):
		"""Verificar todos los algoritmos de compresión con información de texto
		"""
		simple_text	= ("""
						Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas tempus vestibulum ligula. Nam arcu mi, pharetra in lobortis at, facilisis id erat. Nam id libero porttitor nunc venenatis tempus a vel enim. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Duis eu fringilla libero, et fringilla elit. Vestibulum magna leo, vehicula eu tortor sed, malesuada blandit mi. Nam eu nisl dapibus, tempus lacus ac, fermentum ipsum. Fusce vestibulum blandit nisi at scelerisque.
						Aenean aliquam, purus sit amet sodales efficitur, sem urna varius nisi, lobortis molestie velit dolor non ex. Mauris eget diam ut lectus dictum porttitor. Donec pellentesque venenatis dui in maximus. Cras facilisis, velit eget accumsan consectetur, dolor elit convallis massa, in ultricies dui leo eget purus. Integer nec metus euismod, finibus ex in, elementum tellus. Sed facilisis imperdiet leo at pulvinar. Curabitur augue sem, fermentum at orci a, dignissim euismod est. Nunc mollis elementum pellentesque.
						Phasellus ut fringilla augue. Morbi elementum ac purus et finibus. Morbi ullamcorper blandit ultricies. Phasellus euismod interdum urna vel ultrices. Maecenas tristique dapibus augue sed mollis. Maecenas cursus arcu ligula, eget ullamcorper lectus dictum nec. Curabitur ut consectetur tortor. Sed et maximus libero. Quisque consequat ipsum mollis velit elementum venenatis. Curabitur dignissim sapien vehicula pellentesque ullamcorper. Proin luctus eros odio, vitae porta arcu maximus molestie. Morbi maximus libero ut lacus tempor euismod. Praesent sodales aliquam nulla, eget rhoncus mauris luctus finibus. Nunc tempus est ut dui tempor egestas. Morbi pharetra ligula non faucibus posuere. In fringilla fermentum semper.
						Mauris a lorem eget justo efficitur porta. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Donec eget consectetur purus. Maecenas arcu lorem, vehicula id libero nec, consequat aliquam lorem. Morbi at consequat est. In hac habitasse platea dictumst. Maecenas arcu odio, pharetra non pulvinar sed, dapibus commodo mi. Quisque aliquam convallis nisi. Quisque pretium porttitor dui, vitae gravida felis luctus et. Donec odio nunc, condimentum ut turpis a, porta varius nunc. Sed sagittis, tellus id dapibus vehicula, metus libero efficitur ex, et iaculis erat eros eu odio. Duis non cursus risus. Nulla lobortis euismod pretium. Vestibulum auctor arcu ac elit facilisis dictum. Donec a arcu eget turpis finibus tincidunt at a mauris.
						Duis vitae elit mauris. Aliquam molestie maximus erat in malesuada. Quisque vehicula nulla dolor, sed faucibus enim egestas vel. Nunc laoreet hendrerit velit quis bibendum. Donec nunc tortor, faucibus a sagittis in, elementum sit amet diam. Pellentesque hendrerit nisi a risus facilisis tincidunt. Curabitur vitae diam justo. Mauris quis hendrerit dolor.
						""").encode("utf-8")
		c = Compressor()
		for t in c.available_types:
			with self.subTest(i=t[0]):
				c.type = t[0]
				c.level = 1
				tmp = c.compress(simple_text)
				tmp = c.decompress(tmp)
				self.assertEqual(simple_text, tmp)
