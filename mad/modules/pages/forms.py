from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, HiddenField, validators, ValidationError

class ContactForm(Form):
	""" Search form """
	def ver_hum(form, field):
		""" Check if the field's value is a number(integer or floating value) """
		try:
			val = field.data.strip()
			if val and val=="sample_string":
				return True
			raise ValidationError("Invalid verification key.")
		except Exception as e:
			raise ValidationError("Invalid verification key.")

	name = TextField("Name", [validators.DataRequired(message="You should provide a name")])
	email = TextField("Email", [validators.DataRequired(message="You should provide an email"), validators.Email(message="Invalid email"), validators.Length(min=5, max=128, message="")])
	message = TextAreaField("Message", [validators.DataRequired(message="Message can't be empty."), validators.Length(min=10, max=1024, message="Message seems way too short/long (min: 10, max: 1024 characters).")])
	verify_human = HiddenField("HiddenField", [validators.DataRequired(message="Please verify you're human."), ver_hum])