from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, PasswordField, validators

class RegistrationForm(Form):
	""" Registration form """
	name = TextField("Name", [validators.DataRequired(message="Name is required."), validators.Length(min=2, max=64, message="Name can only have 2-64 characters.")])
	email = TextField("Email", [validators.DataRequired(message="Email is required."), validators.Email(message="Invalid email"), validators.Length(min=5, max=128, message="")])
	password = PasswordField("Password", [validators.DataRequired(message="Password cannot be blank."), validators.EqualTo('confirm', message='Passwords must match.')])
	confirm = PasswordField("Repeat Password")
	is_provider = BooleanField("I'm an ad-space provider / publisher.", default=False)

class LoginForm(Form):
	""" Login form """
	email = TextField("Email", [validators.DataRequired(message="Email is required."), validators.Email(message="Invalid email."), validators.Length(min=5, max=128, message="")])
	password = PasswordField("Password", [validators.DataRequired(message="Password cannot be blank.")])
	remember = BooleanField("Remember", default=False)


class UpdateUserData(Form):
	""" Update user data form """
	name = TextField("Name", [validators.DataRequired(message="Name is required."), validators.Length(min=2, max=64, message="Name can only have 2-64 characters.")])
	password = PasswordField("Password", [validators.EqualTo("confirm", message="Passwords must match.")])
	confirm = PasswordField("Repeat Password")