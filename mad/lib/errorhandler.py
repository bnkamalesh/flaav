# -*- coding: utf-8 -*-
from time import strftime

from flask import render_template, url_for, request
from flask.ext.login import current_user

import mad.settings

class ErrorHandler(object):
	def __init__(self):
		pass

	def initiate(self, app):
		self.no_appcontext_error(app)

	def get_error(self, error, occurred_at="", log_file="log"):
		# get a friendly error which can be exposed to the user
		error = str(error)
		self.log_error(error=error, occurred_at=occurred_at, log_file=log_file)
		return {"status": "failed", "message": error}

	def log_error(self, error, occurred_at, log_file):
		# log the error to a file
		try:
			log = open(mad.settings.BASE_DIR+"/logs/"+log_file, 'a')
			if not log:
				log = open(mad.settings.BASE_DIR+"/logs/"+log_file, 'w')

			if log:
				log.write(strftime("%d/%h/%Y : %Hh:%Mm:%Ss") + " occurred at: "+ occurred_at+": "+error +"\n")
			else:
				print "\n\n****Error***\n"
				print "\nOccurred at:"+str(occurred_at)+": "+str(error)
				print "\n******\n\n"
			log.close()
		except Exception as e:
			print "Could not write to log"
			print "Write error: " + str(e)
			print "Error received: " + error

	def no_appcontext_error(self, app):
		"""
		These are critical errors, which occurs when app loses context
		"""
		@app.errorhandler(404)
		@app.errorhandler(400)
		def not_found(error):
			data={}
			data["error_type"] = error
			data["error"] = "You probably got lost in the labyrinth of Internet.<br />Why else would you be here? "+ '<span style="font-style: normal;">¯\_(ツ)_/¯</span>'.decode("utf-8")
			return render_template("error.html", data=data)

		@app.errorhandler(401)
		def not_found(error):
			data={}
			data["error_type"] = error
			data["error"] = "Sorry, you're not authorized to access this page."
			if not current_user.is_authenticated():
				data["error"] += "<br/>Please <a href=\""+url_for("user.index", action="login", next=request.url)+"\">login</a> and try again."

			return render_template("error.html", data=data)

		@app.errorhandler(403)
		def unhandled_error(error):
			data={}
			data["error_type"] = error
			data["error"] = "The URL you entered or the file you're trying to access is forbidden."
			return render_template("error.html", data=data)

		@app.errorhandler(500)
		def internal_error(error):
			""" Error 500 is shown only if debug is turned off, ie, on live version """
			data={}
			data["error_type"] = error
			data["error"] = 'Sorry, something unexpected happened.<br />Please <a href="'+{{ url_for('pages.index', name='contact') }}+'">contact us</a>.'
			return render_template("error.html", data=data)

		@app.errorhandler(Exception)
		def unhandled_error(error):
			data={}
			data["error_type"] = "Unknown"
			data["error"] = 'Sorry, something unexpected happened.<br />Please <a href="'+{{ url_for('pages.index', name='contact') }}+'">contact us</a>.'
			if app.config["DEBUG"]:
				data["error"] += "<br /> Debug Info: " + str(error)
			return render_template("error.html", data=data)

error_handle = ErrorHandler()