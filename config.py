import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # 从DATABASE_URL 环境变量中获取数据库 URL
    # 如果没有定义，则将其配置为 basedir 变量表示的应用顶级目录下的一个名为 app.db 的文件路径  
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                'sqlite:///' + os.path.join(basedir, 'app.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS 配置项用于设置数据发生变更之后是否发送信号给应用
    SQLALCHEMY_TRACK_MODIFICATIONS = False