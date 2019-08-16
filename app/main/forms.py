from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length

from app.models import User


class EditProfileForm(FlaskForm):
    about_me = TextAreaField('关于我', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    post = TextAreaField('说点什么', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('发布')

class SearchForm(FlaskForm):
    keyword = StringField('')
    sumit = SubmitField('搜索')