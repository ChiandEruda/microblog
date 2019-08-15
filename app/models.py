from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin
from hashlib import md5
from flask import current_app

from time import time
import jwt

from app import db
from app import login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

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

    # follow()和unfollow()方法使用关系对象的append()和remove()方法
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    # 有必要在处理关系之前，使用一个is_following()方法来确认操作的前提条件是否符合
    def is_following(self, user):
        # 查找关联表中左侧外键设置为 self 用户且右侧设置为user参数的数据行
        # 查询以 count() 方法结束，返回结果的数量
        # 这个查询的结果是0或1，因此检查计数是1还是大于0实际上是相等的
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    
    # 查看已关注用户的动态  
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        # followed 和 own 查询结果集是在排序之前进行的合并
        return followed.union(own).order_by(Post.timestamp.desc())

    followed = db.relationship(
        # 'User'是关系当中的右侧实体（将左侧实体看成是上级类）
        # 由于这是自引用关系，所以不得不在两侧都使用同一个实体
        # secondary 指定了用于该关系的关联表
        'User', secondary=followers,
        # primaryjoin 指明了通过关系表关联到左侧实体（关注者）的条件
        # follower_id字段与这个关注者的用户ID匹配
        # followers.c.follower_id表达式引用了该关系表中的follower_id列
        primaryjoin=(followers.c.follower_id == id),
        # secondaryjoin 指明了通过关系表关联到右侧实体（被关注者）的条件
        secondaryjoin=(followers.c.followed_id == id),
        # backref定义了右侧实体如何访问该关系
        # 在左侧，关系被命名为 followed
        # 所以在右侧使用 followers 来表示所有左侧用户的列表，即粉丝列表
        # 附加的 lazy 参数表示这个查询的执行模式，设置为动态模式的查询不会立即执行，直到被调用
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
             current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token,  current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Post(db.Model):
    __searchable__ = ['body']
    
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    # 添加了一个 default 参数，并传入了 datetime.utcnow 函数 
    # 当将一个函数作为默认值传入后，SQLAlchemy 会将该字段设置为调用该函数的值
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # user_id字段初始化为user.id的外键
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)