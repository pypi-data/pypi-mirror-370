# Gets triggered when an invalid username is encountered leading to an invalid OUID.
class InvalidOUID(Exception):
	def __init__(self, message):
		self.message = message