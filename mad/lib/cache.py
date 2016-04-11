import time

class CacheHandler:
	""" 
	This class is used to save  frequenctly accessed but,
	rarely changed data of any kind.
	"""
	def __init__(self):
		#global cache, common to all users
		self.data = {}

		#Cache specific to logged in users
		self.user_data = {}

	def get_item(self, name, user_id=None):
		current_epoch = int(time.time())
		if user_id:
			user_id = str(user_id)
			if user_id in self.user_data and name in self.user_data[user_id]:
				if current_epoch < self.users[user_id][name]["expire"]:
					return self.user_data[user_id][name]["value"]
		else:
			if name in self.data:
				if current_epoch < self.data[name]["expire"]:
					return self.data[name]["value"]

		return None

	def set_item(self, name, value, user_id=None, expire_hrs=12):
		""" 
		Set/Update cached data 
		expire_hrs: No.of hrs after which this cache will be cleared
		"""
		if value==None:
			self.delete_item(name)
		else:
			expire_epoch = int(time.time()) + int(expire_hrs*60*60)
			if user_id:
				user_id = str(user_id)
				if not user_id in self.user_data:
					self.user_data[user_id] = {}

				self.user_data[user_id][name] = {"value": value, "expire": expire_epoch}
			else:
				self.data[name] = {"value": value, "expire": expire_epoch}

	def delete_item(self, name, user_id=None):
		if user_id:
			user_id=str(user_id)
			if user_id in self.user_data:
				del(self.user_data[user_id])
		else:
			if name in self.data:
				del(self.data[name])

Cache = CacheHandler()