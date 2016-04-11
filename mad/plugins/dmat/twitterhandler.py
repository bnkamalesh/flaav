import tweepy

class TwitterHandler:
	c_key = "hb2pmpA8AYUv6775rmewxHVkB"
	c_secret = "UEp6i9uVYgdBhNtpkeIGc9Tr3G9TijENKZJeBRG6TCBvVNWCTz"
	a_token = None
	a_secret = None
	auth = tweepy.OAuthHandler(c_key, c_secret)
	request_token = None

	def __init__(self):
		pass

	def get_api(self):
		try:
			a = tweepy.OAuthHandler(self.c_key, self.c_secret)
			a.set_access_token(self.a_token, self.a_secret)
			return tweepy.API(a)
		except Exception as e:
			return {"status": "failed", "message": str(e)}

	def get_req_url(self):
		try:
			url = self.auth.get_authorization_url()
			return [url, self.auth.request_token.key, self.auth.request_token.secret]
		except Exception as e:
			return {"status": "failed", "message": str(e)}

	def set_access_token(self, access_token, access_token_secret):
		try:
			self.a_token = access_token
			self.a_secret = access_token_secret
			self.auth.set_access_token(access_token, access_token_secret)
			return {"status": "success", "message": "Acess token set successfully"}
		except Exception as e:
			return {"status": "failed", "message": str(e)}

	def update_status(self, status_message=None):
		try:
			if not status_message:
				return {"status": "failed", "message": "Empty message"}
			api = self.get_api()
			api.update_status(status_message)
		except Exception as e:
			return {"status": "failed", "message": str(e)}

	def get_user(self, username=None):
		try:
			api = self.get_api()
			if username:
				return api.get_user(username)
			else:
				return api.me()
		except Exception as e:
			return {"status": "failed", "message": str(e)}

	def get_tweets(self, username=None, count=3):
		try:
			api = self.get_api()
			if username:
				return api.user_timeline(username, count=count)
			else:
				return api.home_timeline(count=count)
		except Exception as e:
			return {"status": "failed", "message": str(e)}


	def get_access_token(self, req_token, verifier):
		try:
			self.auth.set_request_token(req_token[0], req_token[1])
			self.auth.get_access_token(verifier)
			return { "access_token": self.auth.access_token.key, "access_token_secret":self.auth.access_token.secret }
		except Exception as e:
			return {"status": "failed", "message": str(e)}
# https://bpaste.net/remove/90525e9c84b1 - removal link