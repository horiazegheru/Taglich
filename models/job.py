class Job:
	def __init__(self, id, job_type, address, description, client_username):
		self.id = id
		self.job_type = job_type
		self.address = address
		self.description = description
		self.client_username = client_username
		self.worker_id = None
		self.done = False

	def assign_worker(self, worker_id):
		self.worker_id = worker_id

	def mark_as_done(self):
		self.done = True

	def __str__(self):
		return str(self.id) + " " + self.job_type + " " + self.address + " " + self.description + " " + self.client_username
