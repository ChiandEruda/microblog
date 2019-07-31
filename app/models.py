from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # 生成 “一” 对 “多” 的类，并为 Post 类反向调用添加 post.author
    posts = db.relationship('Post', backref='author', lazy='dynamic')

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