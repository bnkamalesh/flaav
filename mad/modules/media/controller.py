import datetime
from bson.code import Code
from mad.lib.controller import Controller
from flask.ext.login import current_user

class MediaController(Controller):
	def __init__(self, media_collection_name="media_items"):
		super(self.__class__, self).__init__()
		self.media_collection_name = media_collection_name
		self.geography_collection_name = "geographies"
		self.demography_collection_name = "demographies"
		self.industries_collection_name = "industries"

	def change_collection(self, name, new_col_name):
		if name=="media_items":
			self.media_collection_name = new_col_name

	def get_media_items(self, conditions=None):
		""" Get media items from the DB collection, based on fitlter """
		try:
			items = []
			id_replace_list = ["viewership_industry", "provider_industry", "select_markets", "demography", "geography"]
			for item in self.get_db_items(collection=self.media_collection_name, conditions=conditions):
				for key in id_replace_list:
					if key in item and item[key]:
						dict_list = None
						if key=="viewership_industry" or key=="provider_industry":
							dict_list = self.get_industries(as_list=False)
						elif key=="select_markets" or key=="geography":
							dict_list = self.get_geographies(as_list=False)
						elif key=="demography":
							dict_list = self.get_demographies(as_list=False)

						item[key] = self.replace_with_id(item[key], dict_list, reverse=True)

				items.append(item)
			return items
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.media.get_media_items()")

	def check_duplicate(self, media_item):
		""" Check for duplicate media item """
		try:
			if self.get_db_items(collection=self.media_collection_name, conditions={"name": media_item["name"], "media_type": media_item["media_type"], "ad_name": media_item["ad_name"]}).count() > 0:
				return True
			return False
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.media.check_duplicate()")


	def replace_with_id(self, source_list, dict_list, reverse=False):
		""" Replace the items in source list with its corresponding database ID """
		if not dict_list:
			return source_list

		count = 0
		total = len(source_list)

		for item in dict_list:
			if reverse:
				if item["_id"] in source_list:
					count += source_list.count(item["_id"])
					source_list = [item["name"] if x==item["_id"] else x for x in source_list]
			else:
				if item["name"] in source_list:
					count += source_list.count(item["_id"])
					source_list = [item["_id"] if x==item["name"] else x for x in source_list]

			if count >= total:
				break

		return source_list

	def prepare_media_item(self, form_data=None, no_owner=False):
		""" 
			This function returns a dictionary prepared from form_data,
			ready to be inserted to the database.
		"""
		media_item = {}

		# field names listed in numeric_fields will be converted to 
		# actual Decimal numbers from string
		numeric_fields = ["price", "views", "unique_views", "frequency", "conversion_rate"]

		# the fields in the following list will be converted from string to corresponding DB ID.
		id_replace_list = ["viewership_industry", "provider_industry", "select_markets", "demography"]

		for fieldname, value in form_data.items():
			if type(value) is unicode:
				value = value.strip()
				if fieldname in numeric_fields and value:
					value = float(value)
				else:
					if fieldname in id_replace_list and value:
						items = [x.strip() for x in value.split(',') if x]
						if fieldname=="viewership_industry" or fieldname=="provider_industry":
							value = self.replace_with_id(items, self.get_industries(as_list=False))
						elif fieldname=="select_markets":
							value = self.replace_with_id(items, self.get_geographies(as_list=False))

			media_item.update({fieldname: value})

		if no_owner==False:
			media_item.update({"owner_user_id": current_user.get_userid()})
		#===
		return media_item

	def add_media_item(self, media_item=None):
		""" Add a media item to the DB collection """
		try:
			if media_item!=None and self.check_duplicate(media_item)==False:
				media_item.update({"created_on": datetime.datetime.utcnow()})
				result = self.add_db_item(collection=self.media_collection_name, content=media_item)
				return {"status": "success", "message": "Media item successfully added to the DB.", "_id": str(result["_id"])}

			return {"status": "failed", "message": "No content provided to save to the DB; or duplicate data found.", "_id": None}
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.media.add_media_item()")

	def update_media_item(self, media_item=None, media_id=None, conditions=None):
		""" Update a media item """
		try:
			if not media_id or not media_item:
				return {"status": "failed", "message": "Could not update media item."}

			media_item.update({"updated_on": datetime.datetime.utcnow()})

			if conditions:
				conditions.update({"_id": media_id})
			else:
				conditions = {"_id": media_id}

			self.update_db_item(collection=self.media_collection_name, conditions=conditions, content=media_item, upsert=True)
			return {"status": "success", "message": "Media item updated successfully"}
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.media.update_media_item()")

	def get_industries(self, as_list=False, conditions=None):
		""" Return all the industries """
		try:
			if as_list:
				industries = self.cache_handle.get_item("industries_as_list")

				if not industries:
					industries = self.get_db_distinct_items(collection=self.industries_collection_name, fieldname="name", conditions=conditions)
					self.cache_handle.set_item("industries_as_list", industries)

			else:
				industries = self.cache_handle.get_item("industries")

				if not industries:
					industries = list(self.get_db_items(collection=self.industries_collection_name, conditions=conditions))
					self.cache_handle.set_item("industries", industries)

			return industries
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.media.get_industries()")

	def get_demographies(self, as_list=False, conditions=None):
		""" Return all the demographies """
		try:
			
			demographies = self.cache_handle.get_item("demographies")
			if not demographies:
				demographies = list(self.get_db_items(collection=self.demography_collection_name, conditions=conditions, sort_by=[("group", 1)]))
				self.cache_handle.set_item("demographies", demographies)

			if as_list:
				dem_as_list = self.cache_handle.get_item("demographies_as_list")
				if not dem_as_list:
					groups = {}
					dem_as_list = []
					for item in demographies:
						if not item["group"] in groups:
							groups.update({item["group"]: []})
							dem_as_list.append("Group#"+item["group"])
							
						if item["subgroup"] and not item["subgroup"] in groups[item["group"]]:
							groups[item["group"]].append(item["subgroup"])
							dem_as_list.append("Sub-Group#"+item["subgroup"])

						dem_as_list.append(item["name"])

				return dem_as_list

			return demographies

		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.media.get_demographies()")

	def get_geographies(self, as_list=False, conditions=None):
		""" Return all the geographies """
		try:
			if as_list:
				geographies = self.cache_handle.get_item("geographies_as_list")
				if not geographies:
					geographies = self.get_db_distinct_items(collection=self.geography_collection_name, fieldname="name", conditions=conditions)
					self.cache_handle.set_item("geographies_as_list", geographies)
			else:
				geographies = self.cache_handle.get_item("geographies")
				if not geographies:
					geographies = list(self.get_db_items(collection=self.geography_collection_name, conditions=conditions))
					self.cache_handle.set_item("geographies", geographies)
			return geographies

		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.media.get_geographies()")


	def get_media_statistics(self):
		""" Prepares and returns media item statistics """
		try:
			dbh = self.get_db_handler()
			reducer = Code("""function(media_item, item){ item.count++; }""")
			stat = dbh[self.media_collection_name].group(
					key={"customer_type": 1},
					condition={},
					initial={"count": 0},
					reduce=reducer
					)
			return stat
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.media.get_media_statistics()")