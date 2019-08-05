from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user

from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.auth.forms import ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # current_user变量的值可以是数据库中的一个用户对象
    # Flask-Login 通过 models.py 提供的用户加载函数回调读取
    # 当用户已经登录，重定向到主页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # 验证用户名可能是否有效，或者用户密码是否正确
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        # login_user() 该函数会将用户登录状态注册为已登录
        # 这意味着用户导航到任何未来的页面时
        # 应用都会将用户实例赋值给 current_user 变量
        login_user(user, remember=form.remember_me.data)
        # 读取和处理 URL 中添加的 next 查询字符串参数
        # 应用就可以在登录后使用它来重定向
        next_page = request.args.get('next')
        # 防止 next 参数中插入一个指向恶意站点的URL
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        # next 参数其值是一个相对路径
        # 将会重定向到本应用的这个相对路径
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)   

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))  

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('恭喜，您已注册成功！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)   

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    # 如果用户登录，重定向到主页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('邮件已发，请检查您的邮箱.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                        title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('您的密码已重置.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)