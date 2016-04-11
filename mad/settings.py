import os

VERSION = "1.0"
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
THREADS_PER_PAGE = 2
CSRF_ENABLED     = True

config = {
	"local": {
			"debug": True,
			"db": {
					"host": "127.0.0.1",
					"name": "flaav_com",
					"user": "",
					"password": ""
				},
			"uploads": "static/uploads/"
			},
	"live": {
			"debug": False,
			"db": {
					"host": "127.0.0.1",
					"name": "",
					"user": "",
					"password": ""
				},
			"uploads": ""
			}
}

# change this to "live" to change settings to live server
opt  = "local"
# ==

DEBUG = config[opt]["debug"]
STATIC_PATH = BASE_DIR + "/static"
PLUGINS_PATH = BASE_DIR + "/plugins"
# Secret key is used for CSRF, used by Flask
SECRET_KEY = "sample"
# ==

DB = config[opt]["db"]

# maximum size of uploaded file, in MB
MAX_CONTENT_LENGTH = 1*1048576
# ===