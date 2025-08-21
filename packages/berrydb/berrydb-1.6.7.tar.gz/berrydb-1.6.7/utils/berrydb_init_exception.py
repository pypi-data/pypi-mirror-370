class BerryDBInitializationException(Exception):
	"""
	Exception raised when the BerryDB SDK is used without being properly initialized.

	Attributes:
		message (str): Explanation of the error.
	"""

	def __init__(self, message="BerryDB SDK is not initialized. Please call init() before using the SDK."):
		self.message = message
		super().__init__(self.message)