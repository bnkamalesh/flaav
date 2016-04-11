import operator

from flask.ext.login import current_user
from mad.modules.media.controller import MediaController
from mad.lib.controller import Controller
from model import SearchHistory

class SearchController(Controller):
	def __init__(self):
		super(self.__class__, self).__init__()

	def save_search(self, searchparams=None, title=None):
		""" Save a search """
		try:
			if not searchparams==None and not title==None and current_user.is_authenticated():
				user_id = current_user.get_userid()
				SH = SearchHistory(searchparams=searchparams, user_id=user_id, title=title)

				# Check for search history count > 10, if > 10, replace oldest
				if SH.get(conditions={"user_id": user_id}).count() < 8:
					SH.save()
				else:
					conditions = {"_id": SH.get(conditions={"user_id": user_id}, sort_by=[("created_on", 1)], limit=1)[0]["_id"]}
					SH.update(conditions=conditions, overwrite=True)

				return {"status": "success", "message": "Successfully saved."}

			return {"status": "failed", "message": "Could not save search."}
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.search.save_search()")


	def get_search_history(self):
		""" Get search history of the user """
		try:
			if current_user.is_authenticated():
				SH = SearchHistory()
				return SH.get(conditions={"user_id": current_user.get_userid()}, sort_by=[("created_on", -1)])
			return None
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.search.get_search_history()")


	def delete_search_history(self, search_id=None):
		""" Delete a search history item """
		try:
			if search_id:
				SH = SearchHistory()
				SH.remove(conditions={"_id": search_id})
				return {"status": "success", "message": "Deleted search history entry."}

			return {"status": "failed", "message": "Could not delete search history entry."}
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.search.delete_search_history()")


	def get_search_params(self, search_id=None):
		""" Get search parameters """
		try:
			if search_id:
				return SearchHistory().get(conditions={"_id": search_id}, findone=True)["searchparams"]
			return None
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.search.get_search_params()")


	def prepare_form_data(self, form):
		""" 
		Prepare search form data. Add choices fetched from the database to
		relevant fields.
		"""
		try:
			MC = MediaController()
			demographies = []
			for item in MC.get_demographies(as_list=True):
				if item:
					demographies.append((item, item))
			form["demography"].choices = demographies
			return form
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.search.prepare_form_data()")

	def get_multiplier(self, num_matches, total, threshold=3, increment=0.33):
		""" 
		This function returns a multiplier according to number of 
		matches and the total.
		"""
		x = 1
		if num_matches>threshold:
			x = 1 + increment * float(num_matches - total)
		elif num_matches<threshold:
			x = increment * float(threshold - num_matches)

		if x<0:
			x = 0.001
		return x

	def process_search_results(self, media_items=None, form_data=None):
		""" 
		Process the search results with the algorithm and update each item with 
		respective scores
		media_items : list of media items
		"""
		try:
			if not form_data:
				return media_items

			if media_items:
				#MGAS(MarketingGoalAcquisitionScore)
				results = []
				for media_item in media_items:
					X = self.get_multiplier(num_matches=len(set(form_data["viewership_industry"]).intersection(media_item["viewership_industry"])), total=len(media_item["viewership_industry"]))
					# Y = self.get_multiplier(num_matches=len(set(form_data["viewership_industry"]).intersection(media_item["viewership_industry"])), total=len(media_item["viewership_industry"]))
					A = self.get_multiplier(num_matches=len(set(form_data["demography"]).intersection(media_item["demography"])), total=len(media_item["demography"]))
					B = self.get_multiplier(num_matches=len(set(form_data["geography"]).intersection(media_item["geography"])), total=len(media_item["geography"]))
					CTRM = 0.4*X + 0.2*A + 0.1*B
					CR = (float(form_data["conversion_rate"]))

					CPA = media_item["price"]
					den = media_item["unique_views"]*CTRM*0.02*CR

					if den==0:
						den = CTRM*0.02*CR

					CPA = CPA/den

					CPV = media_item["price"]
					den = media_item["unique_views"]
					if den==0:
						den = 1000

					CPV =  CPV / den

					MGAS = 0
					if form_data["market_goal"]=="Acquisition":
						MGAS = CPA * 0.85 + CPV * 0.15
					elif form_data["market_goal"]=="Awareness":
						MGAS = CPV * 0.85 + CPA * 0.15
					
					MS = 20

					MR = 0
					if MGAS > 0:
						MR = MS / MGAS

					media_item.update({"MR": MR, "MS": MS,"MGAS": MGAS, "CPA": CPA, "X": X, "A": A, "B": B, "CTRM": CTRM, "CPV": CPV, "CR": CR})
					results.append(media_item)
				return sorted(results, key=operator.itemgetter("MR"), reverse=True)

		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.search.process_search_results()")

	def get_search_results(self, form_data=None, start=0, limit=50):
		""" Get search results """
		try:
			if form_data==None:
				return None

			if limit>1000:
				limit = 1000
			if limit < 1:
				limit = 1

			search_query = {"$and": [{"$or": []}]}

			# Preparing search query
			# budget is increased by 10%
			or_cond = {"$or": []}
			for field_name, value in form_data.items():
				if type(value) is list and value:
					search_query["$and"][0]["$or"].append({field_name: {"$in": value}})
				elif field_name=="budget":
					value = float(value)
					search_query["$and"].append({"price": {"$lte": value+(value*0.1)}})
				else:
					search_query["$and"][0]["$or"].append({field_name: value})
			# ==

			MC = MediaController()
			media_items = [item for item in MC.get_media_items(conditions=search_query) if item]
			if media_items:
				media_items = self.process_search_results(media_items, form_data=form_data)

			return media_items
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.search.get_search_results()")