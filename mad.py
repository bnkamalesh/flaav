from cherrypy import wsgiserver
from mad import app

if __name__=="__main__":
	try:
		hosts = {"local": {"host": "localhost", "port": 8082}, "live": {"host": "127.0.0.1", "port": 8082} }
		opt  = "local"

		host = hosts[opt]

		if opt=="local":
			app.run(host=host["host"], port=host["port"], debug=True)
		else:
			app_list = wsgiserver.WSGIPathInfoDispatcher({"/": app})
			server = wsgiserver.CherryPyWSGIServer( (host["host"], host["port"]), app_list)
			server.start()
	except KeyboardInterrupt:
		server.stop()
		print "2.2 Server stopped [ended by user]"
