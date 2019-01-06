class User:
	def __init__(self, id, username, email, password,
				firstname, lastname, dob, description,
				phone_nr, account_type, job_type):

		self.id = id
		self.username = username
		self.email = email
		self.password = password
		self.firstname = firstname
		self.lastname = lastname
		self.dob = dob
		self.description = description
		self.phone_nr = phone_nr
		self.account_type = account_type
		self.job_type = job_type

	def __str__(self):
		return str(self.id) + " " + self.username + " " + self.firstname + " " + self.lastname + " " + str(self.dob) + " " + self.description + " " + self.phone_nr + " " + self.account_type