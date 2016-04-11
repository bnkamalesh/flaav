from flask import Flask

from mad.lib import loginmanager
from mad.lib import errorhandler 

error_handle = errorhandler.ErrorHandler()
try:
	app = Flask(__name__)
	app.config.from_object("mad.settings")

	loginmanager.config_LM(app)
	error_handle.initiate(app)

	# Register blueprints
	from mad.modules.pages import pages
	app.register_blueprint(pages)

	from mad.modules.user import user
	app.register_blueprint(user)

	from mad.modules.media import media
	app.register_blueprint(media)

	from mad.modules.search import search
	app.register_blueprint(search)

	from mad.modules.dashboard import dashboard
	app.register_blueprint(dashboard)

	from mad.modules.pluginloader import pluginloader
	app.register_blueprint(pluginloader)
	# ===
except Exception as e:
	error_handle.get_error(error=str(e), occurred_at="mad.init()")