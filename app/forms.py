from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FloatField, IntegerField, DateField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from app.models import User

# Registration Form
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# Listing Form
class ListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=20, max=2000)])
    address = StringField('Address', validators=[DataRequired(), Length(max=300)])
    city = StringField('City', validators=[DataRequired()], default='San Jose')
    state = StringField('State', validators=[Length(max=2)], default='CA')
    zip_code = StringField('ZIP Code', validators=[Length(max=10)])
    price_per_month = FloatField('Price per Month ($)', validators=[DataRequired(), NumberRange(min=0)])
    bedrooms = IntegerField('Bedrooms', validators=[DataRequired(), NumberRange(min=0, max=10)])
    bathrooms = FloatField('Bathrooms', validators=[DataRequired(), NumberRange(min=0, max=10)])
    square_feet = IntegerField('Square Feet', validators=[NumberRange(min=0)])
    available_from = DateField('Available From', validators=[DataRequired()], format='%Y-%m-%d')
    available_to = DateField('Available To', format='%Y-%m-%d')
    amenities = TextAreaField('Amenities (comma-separated)')
    submit = SubmitField('Create Listing')

# Booking Form
class BookingForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    message = TextAreaField('Message to Owner', validators=[Length(max=500)])
    submit = SubmitField('Book')

    def validate_end_date(self, field):
        if field.data <= self.start_date.data:
            raise ValidationError('End date must be after start date')

# Review Form
class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        ('5', '5 Stars - Excellent'),
        ('4', '4 Stars - Good'),
        ('3', '3 Stars - Average'),
        ('2', '2 Stars - Poor'),
        ('1', '1 Star - Terrible')
    ], validators=[DataRequired()])
    comment = TextAreaField('Review', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Submit Review')

# Search Form
class SearchForm(FlaskForm):
    search = StringField('Search')
    min_price = FloatField('Min Price', validators=[NumberRange(min=0)], default=0)
    max_price = FloatField('Max Price', validators=[NumberRange(min=0)], default=10000)
    city = StringField('City')
    state = StringField('State', validators=[Length(max=2)])
    submit = SubmitField('Search')
