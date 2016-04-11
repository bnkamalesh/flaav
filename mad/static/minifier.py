import os

CSS = []
JS = []
location = os.getcwd()
plugins_js = []
plugins_css = []
try:
	for root, dirs, files in os.walk(location+"/plugins"):
		for f in files:
			fullpath = os.path.join(root, f)
			if os.path.splitext(fullpath)[1].lower()==".js":
				f = open(fullpath, "r")
				text = f.read()
				f.close()
				plugins_js.append(text + '\n\n')
			elif os.path.splitext(fullpath)[1].lower()==".css":
				f = open(fullpath, "r")
				text = f.read()
				f.close()
				plugins_css.append(text + '\n\n')

	print "".join(plugins_css)
except Exception as e:
	print str(e)