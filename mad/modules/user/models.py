from sqlalchemy import Column, String, Integer, Date
from mad.lib.model import Model

class Users(Model):
	""" Users table data model, for login users """
	__tablename__ = "users"

	id = Column(Integer, primary_key=True)
	email = Column(String, nullable=False)
	password = Column(String, nullable=False)
	name = Column(String)