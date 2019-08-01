from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin
from hashlib import md5

from app import db
from app import login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    # 生成 “一” 对 “多” 的类，并为 Post 类反向调用添加 post.author
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        # 生成用户的电子邮件地址的 MD5 哈希值
        # Python 中的 MD5 的参数类型需要是字节而不是字符串
        # 所以在将字符串传递给该函数之前，需要将字符串编码为字节
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    # 添加了一个 default 参数，并传入了 datetime.utcnow 函数 
    # 当将一个函数作为默认值传入后，SQLAlchemy 会将该字段设置为调用该函数的值
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # user_id字段初始化为user.id的外键
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)