from bson.objectid import ObjectId
from pymongo import MongoClient
from flask import current_app
from errorhandler import ErrorHandler
from cache import Cache

class Controller(object):
	""" Parent class to all Controller classes. """
	def __init__(self):
		self.error_handle = ErrorHandler()
		self.cache_handle = Cache

	def get_db_handler(self):
		""" Returns the DB handler """
		mc = MongoClient()
		return mc[current_app.config["DB"]["name"]]

	def add_db_item(self, collection=None, content=None, _id=None, upsert=False):
		""" Save an item to the DB """
		try:
			if collection and content:
				db = self.get_db_handler()
				_id = db[collection].save(content)
				return {"status": "success", "message": "Successfully added item to the DB", "_id": _id}
			return None
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.lib.controller.add_db_item()")

	def update_db_item(self, collection=None, conditions=None, content=None, upsert=False, overwrite=False, noobjectify=False, multi=False):
		""" Update/upsert a DB item """
		try:
			if collection and conditions and content:
				db = self.get_db_handler()
				if noobjectify==False and "_id" in conditions:
					conditions["_id"] = ObjectId(conditions["_id"])
				if overwrite:
					db[collection].update(conditions, {"$set": content}, upsert=upsert, multi=multi)
				else:
					db[collection].update(conditions, content, upsert=upsert, multi=multi)
			return {"status": "success", "message": "DB item updated successfully."}
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.lib.controller.update_db_item()")


	def get_db_items(self, collection=None, conditions=None, sort_by=[("_id", 1)]):
		""" Get items from a collection in the DB and return results """
		try:
			if collection:
				if conditions and "_id" in conditions:
					# By default, if an _id is provided, it'll be converted into an ObjectId instance.
					# "noobjectify" would prevent it from making use of the _id directly instead of 
					# converting it into an ObjectId instance.
					if not "noobjectify" in conditions or conditions["noobjectify"]==False:
						conditions.update({"_id": ObjectId(conditions["_id"])})
				items = self.get_db_handler()[collection].find(conditions).sort(sort_by)
				if items:
					return items
			return None
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.lib.controller.get_db_items()")

	def get_db_distinct_items(self, collection=None, fieldname=None, conditions=None, sort_by=[("_id", 1)]):
		""" Get unique/distinct values from all records of the given field """
		try:
			if collection and fieldname:
				return self.get_db_handler()[collection].find(conditions).sort(sort_by).distinct(fieldname)
			return None
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.lib.controller.get_db_distinct_items()")
			

	def remove_db_item(self, collection=None, conditions=None, remove_all=False):
		""" Remove an or all items from the collection, based on given conditions """
		try:
			if remove_all:
				conditions = {}

			if collection and conditions:
				self.get_db_handler()[collection].remove(conditions)

			return {"status": "success", "message": "Successfully removed item(s) from the DB"}
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.lib.controller.remove_db_item()")