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

class RequiredIf(validators.Required):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)

class SettingsForm(Form):
	post_frequency = SelectField("Posting frequency",
								 [validators.DataRequired(message="You need to choose a posting frequency.")],
								 choices=[("Once a week", "Once a week"), ("None", "None")])

class GroupEntryForm(Form):
	""" Add a new group """
	level = TextField("Group level", validators=[validators.DataRequired("Group level is required"), isInt])
	group = TextField("Group name", validators=[validators.DataRequired("Group name is required")])
	parent_group = HiddenField("Group parent")
	parent_level = HiddenField("Group parents", validators=[isInt, RequiredIf("parent_group")])

class NewWordForm(Form):
	""" Add a new word """
	word_type = TextField("Word type", validators=[validators.DataRequired("Word type is required")])
	word_group = TextField("Word group", validators=[validators.DataRequired("Word group is required")])
	word = TextField("Word", validators=[validators.DataRequired("Word group is required")])

class NewTweetForm(Form):
	""" Add a new tweet """
	tweet = TextAreaField("Tweet", validators=[validators.DataRequired("A tweet is required")])
	group = HiddenField("Tweet group/category", validators=[validators.DataRequired("A group/category is required")])
	group_level = HiddenField("Tweet group level", validators=[validators.DataRequired("Group level is required")])