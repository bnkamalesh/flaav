import re
from flask.ext.wtf import Form
from wtforms import HiddenField, SelectField, RadioField, TextField, validators, SelectMultipleField, widgets, ValidationError

class MultiCheckboxField(SelectMultipleField):
	widget = widgets.ListWidget(prefix_label=False)
	option_widget = widgets.CheckboxInput()

class SearchForm(Form):
	""" Search form """
	def isNum(form, field):
		""" Check if the field's value is a number(integer or floating value) """
		try:
			val = field.data.strip()
			if val:
				float(val)
			return True
		except ValueError:
			raise ValidationError("Invalid number provided(only numbers and 1 period allowed).")

	def numRange(minimum=0, maximum=0):
		""" Check if the value is in between min and max """
		def _numRange(form, field):
			try:
				value = float(field.data.strip())
				if value>=minimum and value<=maximum:
					return True
				else:
					raise ValidationError("Invalid value provided or value out of range.")
			except ValidationError:
				raise ValidationError("Invalid number provided(only numbers and 1 period allowed).")

		return _numRange

	market_goal = SelectField("What is the most common purpose of your advertisement?", [validators.DataRequired(message="A marketing goal is required.")], choices=[("Acquisition", "Acquisition"), ("Retention", "Retention"), ("Awareness", "Awareness")])
	customer_type = RadioField("Do you focus on Business to Business or Business to Consumer?", [validators.DataRequired(message="You need to choose a  business type.")], choices=[("B2B", "Business to Business (B2B)"), ("B2C", "Business to Consumer (B2C)"), ("Both", "Both")])
	budget = TextField("What is your budget?", [validators.DataRequired(message="Budget is required."), isNum])
	viewership_industry = TextField("Which industry should your ad target?")
	campaign_length = SelectField("How long are you willing to run this campaign?",
									[validators.DataRequired(message="You need to choose a campaign length.")], 
									choices=[("Just once", "Just once"), ("1 week", "1 week"), ("1 month", "1 month / 4 weeks"), ("3 months", "1 Quarter / 3 months"), ("1 year", "1 year"), ("custom", "Custom range")])
	media_type = MultiCheckboxField("Type of Marketing Media?", choices=[("blogs", "Blogs"), ("billboard", "Billboard"), ("public transport", "Public Transport"), ("internet ads", "Internet ads"), ( "magazines", "Magazines"), ("newspapers", "Newspapers"), ("social media", "Social Media")])
	demography = MultiCheckboxField("What demographies are you targetting?", choices=[])
	geography = MultiCheckboxField("What geographic area are you targetting?", choices=[("Local", "Local"), ("Select markets", "Select markets"), ("National", "National"), ("International", "International"), ("All", "All")])
	select_markets = TextField("Which markets(cities/locations) would you like to cover?")
	conversion_rate = TextField("How good are you at converting your viewers?", [isNum, numRange(minimum=0.5, maximum=7)], default=0.5)

class SaveSearchForm(Form):
	""" Save search form """
	title = TextField("Title", [validators.DataRequired(message="Title is required")])
	searchparams = HiddenField("Search parameters", [validators.DataRequired(message="Search parameters is required")])