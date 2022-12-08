from wtforms import StringField, SubmitField, EmailField, PasswordField, DateField, SelectField, FileField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
# from flask_uploads import UploadSet, IMAGES
from flask_wtf.file import FileField, FileAllowed, FileRequired


# forms
class Registration(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class Login(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class Add_Products(FlaskForm):
    product_name = StringField("Product Name", validators=[DataRequired()])
    product_description = StringField("Product Description", validators=[DataRequired()])
    product_price = StringField("Product Price", validators=[DataRequired()])
    product_img = FileField("Upload Product Image", validators=[FileRequired(),
                                                                FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])

    submit = SubmitField("Submit")


class Check_Out(FlaskForm):
    Name = StringField("Name", validators=[DataRequired()])
    Address = StringField("Address", validators=[DataRequired()])
    Card_NO = StringField("Card Number", validators=[DataRequired()])
    CVV = StringField("CVV", validators=[DataRequired()])
    EXP = StringField("EXP. Date", validators=[DataRequired()])
    Zip_Code = StringField("Zip Code", validators=[DataRequired()])
    submit = SubmitField("Submit")


