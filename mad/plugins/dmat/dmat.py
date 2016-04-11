import re
import os
import imp

from mad.lib.plugin import Plugin
from flask import url_for, request, session
from flask_oauth import OAuth


abspath = os.path.dirname(os.path.abspath(__file__))+'/'

class DMAT(object, Plugin):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.id = "dmat"
		self.required_roles = ["subscriber"]
		self.plugin_templates = abspath.split('/')[-2]+"/templates/"
		# loading modules from plugin directory
		self.forms = imp.load_source("forms", abspath+"forms.py")
		th = imp.load_source("twitterhandler", abspath+"twitterhandler.py")
		self.twitterhandler = th.TwitterHandler()

	def plugin_home(self):
		st = self.get_settings()
		data = {}
		if st and "twitter_screen_name" in st:
			self.twitterhandler.set_access_token(access_token=st["access_token"], access_token_secret=st["access_token_secret"])
			data.update({"tweets": self.twitterhandler.get_tweets(username=st["twitter_screen_name"]), "twitter_name": st["twitter_name"], 
						 "twitter_screen_name": st["twitter_screen_name"], "profile_image": st["profile_image_url_https"]})
		return self.render_plugin(template_src=self.plugin_templates+"home.html", data = data)

	def prepare_form_from_data(self, form=None, data=None):
		""" Set the values for form fields, with the data provided """
		try:
			if form and data:
				for key, value in data.items():
					if key in form:
						form[key].data = value
			return form
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.plugins.dmat.prepare_form_from_data()")


	def plugin_settings(self, params=None, form=None):
		""" This function should return HTML for the plugin's settings page. """
		try:
			get_item = params.get("get")
			if get_item=="groups":
				groups = []
				for item in self.get_data(conditions={"data_type": "group"}, sort_by=[("level", 1), ("group", 1)], user_specific=False):
					groups.append({"group": item["group"], "level": item["level"]})

				return {"groups": groups}

			elif get_item=="words":
				words = {}
				for item in self.get_data(conditions={"data_type": "word"}, user_specific=False):
					if not item["word_type"] in words:
						words.update({item["word_type"]: {} })
					if not item["word_group"] in words[item["word_type"]]:
						words[item["word_type"]].update({item["word_group"]: []})

					words[item["word_type"]][item["word_group"]].append(item["word"])
				return {"words": words}

			elif get_item=="twitter-auth-url":
				resp = self.twitterhandler.get_req_url()
				if "status" in resp:
					return self.error_handle.get_error(error=str(resp), occurred_at="Retrieving twitter authorization URL.")
					# return {"message": "Couldn't retrieve request URL", "status": "failed"}
				else:
					session["req_token"] = [resp[1], resp[2]]
					return {"url": resp[0]}

			elif get_item=="twitter-callback":
				sf_settings = self.get_settings()
				if not type(sf_settings) is dict:
					sf_settings = {}

				access_tokens = self.twitterhandler.get_access_token(session["req_token"], request.args.get("oauth_verifier"))
				sf_settings.update(access_tokens)
				session.pop("req_token", None)

				self.twitterhandler.set_access_token(access_token=access_tokens["access_token"], access_token_secret=access_tokens["access_token_secret"])
				me = self.twitterhandler.get_user()
				sf_settings.update({"profile_image_url_https": me.profile_image_url_https, "twitter_screen_name": me.screen_name, "twitter_name": me.name})
				self.save_settings(settings=sf_settings)
				html = '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Twitter callback</title><script>if(opener!==null){opener.DMAT.close_auth_window();}</script></head><body></body></html>'
				return html

			else:
				SF = self.forms.SettingsForm(form)
				NGF = self.forms.GroupEntryForm(form)
				NWF = self.forms.NewWordForm(form)
				NTF = self.forms.NewTweetForm(form)
				sf_settings = self.get_settings()

				if not type(sf_settings) is dict:
					sf_settings = {}

				data = {}

				set_type = params.get("settings-type")

				if set_type and form:
					if set_type=="posting-frequency":
						if SF.validate():
							sf_settings.update(SF.data)
							self.save_settings(settings=sf_settings)
							data.update({"message": "Posting frequency updated successfully", "status": "success"})

					elif set_type=="new-group":
						self.required_roles = ["admin"]
						if NGF.validate() and self.check_role():
							new_group = NGF.data
							new_group.update({"data_type": "group"})
							new_group["level"] = int(new_group["level"])

							flag = True
							if new_group["parent_level"]:
								new_group["parent_level"] = int(new_group["parent_level"])
								if new_group["parent_level"] > new_group["level"]:
									data.update({"status": "failed", "message": "Incorrect parent provided"})
									flag = False

							if flag:
								result = self.save_data(data=new_group, user_specific=False, allow_duplicate=False, 
														dup_fields={"level": new_group["level"], "group": new_group["group"]})
								if result["status"]=="success":
									data.update({"message": "New group added successfully", "status": "success" })
								else:
									data.update({"message": result["message"], "status": "failed" })

					elif set_type=="new-word":
						if NWF.validate():
							new_word = NWF.data
							new_word.update({"data_type": "word"})
							result = self.save_data(data=new_word, user_specific=False, allow_duplicate=False, 
													dup_fields={"word": new_word["word"], "word_group": new_word["word_group"], "word_type": new_word["word_type"]})
							if result["status"]=="success":
								data.update({"message": "New word added successfully", "status": "success"})
							else:
								data.update({"message": result["message"], "status": "failed" })

					elif set_type=="new-tweet":
						if NTF.validate():
							new_tweet = NTF.data
							new_tweet.update({"data_type": "tweet"})
							pattern = re.compile(r"""(\[(.*?)\])""")
							tweet = new_tweet["tweet"]
							new_tweet.update({"tweet": pattern.sub("[#]", tweet), "replacements": []})
							for item in pattern.finditer(tweet):
								parts = item.group(2).split("***")
								if parts:
									parts[0] = parts[0].strip()
									parts[1] = parts[1].strip()
									new_tweet["replacements"].append({"word_type": parts[0], "word_group": parts[1]})

							result = self.save_data(data=new_tweet, user_specific=False, allow_duplicate=False, 
													dup_fields={"tweet": new_tweet["tweet"], "group": new_tweet["group"], "group_level": new_tweet["group_level"]})
							# Find replace positions and word pools
							if result["status"]=="success":
								data.update({"message": "New tweet saved successfully.", "status": "success"})
							else:
								data.update({"message": result["message"], "status": "failed" })

				elif set_type=="new-word-export":
						for line in open(os.getcwd()+"/mad/plugins/dmat/export/word-list.csv", "r"):
							parts = line.split(",")
							for i in xrange(0, 3):
								parts[i] = parts[i].strip()

							if parts[0] and parts[1] and parts[2]:
								new_word = {"word_type": parts[0], "word_group": parts[1], "word": parts[2]}
								new_word.update({"data_type": "word"})
								result = self.save_data(data=new_word, user_specific=False, allow_duplicate=False, 
														dup_fields={"word": new_word["word"], "word_group": new_word["word_group"], "word_type": new_word["word_type"]})
								if not result["status"]=="success":
									print "Failed:" + result["message"]
							else:
								print "Invalid data, line: "+str(line)

						print "\n\nFinished exporting\n\n"

				# elif set_type=="twitter-callback":
				# 	access_tokens = self.twitterhandler.get_access_token(session["req_token"], request.args.get("oauth_verifier"))
				# 	sf_settings.update(access_tokens)
				# 	session.pop("req_token", None)

				# 	self.twitterhandler.set_access_token(access_token=access_tokens["access_token"], access_token_secret=access_tokens["access_token_secret"])
				# 	me = self.twitterhandler.get_user()
				# 	sf_settings.update({"profile_image_url_https": me.profile_image_url_https, "twitter_screen_name": me.screen_name, "twitter_name": me.name})
				# 	self.save_settings(settings=sf_settings)

				
				if "profile_image_url_https" in sf_settings:
					data.update({"profile_image_url_https": sf_settings["profile_image_url_https"]})

				if "twitter_screen_name" in sf_settings:
					data.update({"twitter_screen_name": sf_settings["twitter_screen_name"]})

				if "twitter_name" in sf_settings:
					data.update({"twitter_name": sf_settings["twitter_name"]})

				SF = self.prepare_form_from_data(form=SF, data=sf_settings)
				data.update({"settingsform": SF, "newgroupform": NGF, "newwordform": NWF, "newtweetform": NTF})
				return self.render_plugin(template_src=self.plugin_templates+"settings.html", data=data)

		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.plugins.dmat.plugin_settings()")

		def generate_tweet(self):
			"""
			Generate tweets
			- Should maintain tweet history (to prevent duplicates)
			- Should check character length
			- If there's a link in the tweet, character length should be < 118, if https, then 117
			"""
			pass

	def main(self):
		try:
			pass
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.plugins.dmat.main()")
