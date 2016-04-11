from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import current_app
from errorhandler import ErrorHandler

class Model(object):
	""" Base class to all Models """
	def __init__(self):
		self.db_name = current_app.config["DB"]["name"]
		self.collection_name = ""
		self.content = None
		self.error_handle = ErrorHandler()

	def set_content(self):
		""" 
			There should be a definition of this function in every child class.
			This function prepares a dictionary of the child class object's parameters which
			are to be saved, and set it to self.content
		"""
		pass
	def set_objprops(self, data=None):
		"""
			This function should have a definition in a child class for when 
			a single result is expected from the DB query. (when findone=True).
			Eg: When fetching a user from the DB.

			This function should then populate the appropriate properties of the object
			with the data fetched from the DB
		"""
		pass


	def get_db_handler(self):
		""" Return DB handler for the appropriate collection, returns None if no collection name provided """
		if not self.collection_name=="":
			return MongoClient()[self.db_name][self.collection_name]
		else:
			return None

	def check_duplicate(self, fields):
		"""
			provided fields, this function will return true if there is a duplicate entry
			false if no duplicate value found
			eg: fields = {"name": "John", "age": 20}
		"""
		try:
			dbh = self.get_db_handler()
			if dbh.find(fields).count()>0:
				return True
			return False
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.lib.Model.check_duplicate()")

	def get(self, conditions=None, sort_by=[("_id", 1)], distinct=False, distinct_fieldname=None, limit=0, findone=False):
		""" Return db items fullfilled by conditions, and sorted by ID """
		try:
			dbh = self.get_db_handler()
			content = None
			if conditions and "_id" in conditions:
				if not "noobjectify" in conditions or conditions["noobjectify"]==False:
					conditions.update({"_id": ObjectId(conditions["_id"])})
				if "noobjectify" in conditions:
					del conditions["noobjectify"]

			if distinct==True and distinct_fieldname:
				content = dbh.find(conditions).sort(sort_by).distinct(distinct_fieldname)
			elif findone==True:
				content = dbh.find_one(conditions)
			else:
				content = dbh.find(conditions).sort(sort_by)

			if content and limit>0:
				content = content.limit(limit)

			return content
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.lib.Model.get()")

	def save(self, duplicate_fields_check=None, allow_duplicate=False):
		""" Add a new item to the collection """
		try:
			# duplicate_fields_check should be a dict, with field and its corresponding value
			self.set_content()

			if not self.content==None:
				if allow_duplicate==False and not duplicate_fields_check==None:
					if self.check_duplicate(fields=duplicate_fields_check)==True:
						return {"status": "failed", "message": "Could not save item. Duplicate entry found."}

				dbh = self.get_db_handler()
				dbh.save(self.content)
				return {"status": "success", "message": "Successfully added item to the DB"}

			return {"status": "failed", "message": "Content is empty" }

		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.lib.Model.save()")

	def update(self, conditions={}, overwrite=False, upsert=False, noobjectify=False, multi=False):
		""" Update a DB entry """
		try:
			self.set_content()

			dbh = self.get_db_handler()
			if "_id" in conditions or "_id" in self.content:
				if not "noobjectify" in conditions or conditions["noobjectify"]==False:
					if not "_id" in conditions:
						conditions.update({"_id": ObjectId(self.content["_id"])})
						del self.content["_id"]
					else:
						conditions.update({"_id": ObjectId(conditions["_id"])})

				#remove "noobjectify" from conditions, since it should not be used in update query
				if "noobjectify" in conditions:
					del conditions["noobjectify"]

			if overwrite:
				dbh.update(conditions, self.content, upsert=upsert, multi=multi)
			else:
				dbh.update(conditions, {"$set": self.content}, upsert=upsert, multi=multi)

			return {"status": "success", "message": "DB item updated successfully."}
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.lib.Model.update()")


	def remove(self, conditions=None, remove_all=False):
		""" Remove 1 or more items from the collection """
		try:
			if remove_all==True:
				conditions = {}
			elif not conditions==None:
				if "_id" in conditions:
					if not "noobjectify" in conditions or conditions["noobjectify"]==False:
						conditions.update({"_id": ObjectId(conditions["_id"])})
					
					#remove "noobjectify" from conditions, since it should not be used in update query
					if "noobjectify" in conditions:
						del conditions["noobjectify"]

				self.get_db_handler().remove(conditions)
			return {"status": "success", "message": "Successfully removed item(s) from the DB"}
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.lib.Model.remove()")