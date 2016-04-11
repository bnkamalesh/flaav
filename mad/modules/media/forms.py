import re
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, BooleanField, RadioField, SelectField, SelectMultipleField, validators, widgets, ValidationError

from controller import MediaController

class MultiCheckboxField(SelectMultipleField):
	widget = widgets.ListWidget(prefix_label=False)
	option_widget = widgets.CheckboxInput()

class AddMediaForm(Form):
	""" Form to add a new media item """
	def isNum(form, field):
		""" Check if the field"s value is a number(integer or floating value) """
		try:
			val = field.data.strip()
			if val:
				float(val)
			return True

		except ValueError:
			raise ValidationError("Invalid number provided(only numbers and 1 period allowed)")

	def removeValidators(self, field, validator_names=None):
		""" Remove validator from the field's validator list """
		if not validator_names:
			return field

		for i in xrange(0, len(validator_names)):
			if validator_names[i]=="DataRequired":
				validator_names[i] = validators.DataRequired

		field.validators = [x for x in field.validators if not type(x) in validator_names]
		return field


	name = TextField("Business name", [validators.DataRequired(message="You should provide a business name")])
	description = TextAreaField("Description of your business", [validators.DataRequired(message="You should provide a description")])
	location = TextField("Location of your business")
	website = TextField("Full URL to your website")
	banner = TextField("Full URL to the company logo")
	email = TextField("Contact E-mail", [validators.DataRequired(message="Email is required"), validators.Email(message="Invalid email"), validators.Length(min=5, max=128, message="")])
	contact_name = TextField("Contact name", [validators.DataRequired(message="Contact person's name is required")])
	contact_phone = TextField("Contact Phone XXX-XXX-XXXX")
	price = TextField("Cost for your most commonly purchased advertisement", [validators.DataRequired(message="Price is required"), isNum])
	views = TextField("Approximate number of views your ad gets", [isNum])
	unique_views = TextField("Average number of unique views", [isNum])
	ad_name = TextField("Advertisement name", [validators.DataRequired(message="Ad-name is required")])
	ad_details_url = TextField("Full URL to the advertising page of your Media Kit")
	media_type = MultiCheckboxField("Type of Marketing Media?", choices=[("Blogs", "Blogs"), ("Billboard", "Billboard"), ("Public transport", "Public transport"), ("Internet ads", "Internet ads"), ( "Magazines", "Magazines"), ("Newspapers", "Newspapers"), ("Social Media", "Social Media"), ("Other", "Other")])
	custom_media_type = TextField("Type of Marketing Media")
	market_goal = SelectField("What is the most common purpose customers advertise with you?", [validators.DataRequired(message="A marketing goal is required")], choices=[("Acquisition", "Acquisition"), ("Awareness", "Awareness"), ("Retention", "Both")])
	customer_type = RadioField("Do you focus on Business to Business or Business to Consumer?", choices=[("B2B", "Business to Business (B2B)"), ("B2C", "Business to Consumer (B2C)"), ("Both", "Both")])
	campaign_length = SelectField("How long is the average campaign?",
									[validators.DataRequired(message="You need to choose a campaign length")], 
									choices=[("Just once", "Just once"), ("1 week", "1 week"), ("1 month", "1 month / 4 weeks"), ("3 months", "1 Quarter / 3 months"), ("1 year", "1 year"), ("custom", "Custom range")])
	provider_industry = TextField("What industry or keywords would you use to describe your marketing outlet? (comma separated)", [validators.DataRequired(message="You should specify at least one industry")])
	viewership_industry = TextField("What are the industries or keywords that describe your viewership? (comma separated)", [validators.DataRequired(message="You should specify at least one industry/keyword")])
	demography = MultiCheckboxField("What demographies do you target best?", [validators.DataRequired(message="You need to specify at least 1 demography")], choices=[])
	geography = MultiCheckboxField("What geographic area do you target best?", [validators.DataRequired(message="You need to specify at least 1 geography")], choices=[("Local", "Local"), ("Select markets", "Select markets"), ("National", "National"), ("International", "International"), ("All", "All")])
	select_markets = TextField("Which markets(cities/locations) would you like to cover?")