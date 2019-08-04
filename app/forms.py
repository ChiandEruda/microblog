from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms import BooleanField
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import Length

from app.models import User

class LoginForm(FlaskForm):
    username = StringField('用户名称', validators=[DataRequired(message='用户名称不能为空')])
    password = PasswordField('用户密码', validators=[DataRequired(message='用户密码不能为空')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')

class RegistrationForm(FlaskForm):
    username = StringField('用户名称', validators=[DataRequired(message='用户信息不能为空')])
    email = StringField('注册邮箱', validators=[DataRequired(message='注册邮箱不能为空'), Email()])
    password = PasswordField('用户密码', validators=[DataRequired(message='用户密码不能为空')])
    password2 = PasswordField(
        '确认密码', validators=[DataRequired(message='确认密码不能为空'), EqualTo('password')])
    submit = SubmitField('注册')

    # 当添加任何匹配模式 validate_ <field_name> 的方法时
    # WTForms 将这些方法作为自定义验证器
    # 并在已设置验证器之后调用它们
    # 确保用户输入的username和email不会与数据库中已存在的数据冲突
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        # 构造方法中的初始值无法继承
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('此用户名无法使用.')

class PostForm(FlaskForm):
    post = TextAreaField('说点什么', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('发布')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message='邮箱不能为空'), Email()])
    submit = SubmitField('发起重置')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('重置密码', validators=[DataRequired(message='重置密码不能为空')])
    password2 = PasswordField(
        '确认密码', validators=[DataRequired(message='确认密码不能为空'), EqualTo('password')])
    submit = SubmitField('确定重置')