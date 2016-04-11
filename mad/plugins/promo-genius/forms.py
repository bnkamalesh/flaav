from flask.ext.wtf import Form
from wtforms import HiddenField, SelectField, RadioField, TextField, TextAreaField, validators, ValidationError

def isInt(form, field):
		""" Check if the field's value is a number(integer) """
		try:
			val = field.data.strip()
			if val:
				int(val)
			return True
		except ValueError:
			raise ValidationError("Invalid integer provided")

class NewPromoForm(Form):
 	""" Add a new promotion """
	promo_title = TextField("Title", validators=[validators.DataRequired("You should provide a title")])
	promo_dates = TextField("Dates", validators=[validators.DataRequired("You should provide at least 1 date")])
	promo_duration = TextField("Days")
	promo_time = TextField("Times", validators=[validators.DataRequired("You should provide at least 1 hr in 24hr format")])
	promo_offer = TextField("Offer name", validators=[validators.DataRequired("You should provide a name for the offer")])
	promo_description = TextAreaField("Offer description", validators=[validators.DataRequired("You should provide a description for the offer")])
	promo_count = TextField("Offer count", validators=[validators.DataRequired("You should provide a count for the number of times this offer can be availed"), isInt])
	reference_boost = SelectField("Increase offer for sharing with friends/reference?", choices = [("yes", "Yes"), ("no", "No")])
	integrate_dmat = SelectField("Integrate with DMAT?", choices = [("yes", "Yes"), ("no", "No")])