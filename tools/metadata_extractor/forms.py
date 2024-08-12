from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SelectMultipleField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import CheckboxInput, ListWidget

class LoginForm(FlaskForm):
    """
    Form for user login to access DHIS2 programs.
    """
    url = StringField('DHIS2 URL', validators=[DataRequired(), Length(max=255)])
    username = StringField('Username', validators=[DataRequired(), Length(max=255)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProgramSelectionForm(FlaskForm):
    """
    Form for selecting a DHIS2 program to work with.
    """
    program = SelectField('Program', choices=[], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Select Program')

class MetadataSelectionForm(FlaskForm):
    """
    Form for selecting metadata types and stages for extraction.
    """
    metadata_types = SelectMultipleField(
        'Metadata Types',
        choices=[
            ('attributes', 'Attributes'),
            ('data-elements', 'Data Elements'),
            ('program-indicators', 'Program Indicators'),
            ('option-sets', 'Option Sets')
        ],
        validators=[DataRequired()],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False)
    )
    stages = SelectMultipleField(
        'Stages',
        choices=[],  # To be populated dynamically
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False)
    )
    submit = SubmitField('Extract Metadata')

class ToolRequestForm(FlaskForm):
    """
    Form for submitting a tool request.
    """
    request_text = TextAreaField('Request', validators=[DataRequired(), Length(max=5000)])
    submit = SubmitField('Submit Request')
