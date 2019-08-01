from flask import render_template
from app import app
from app import db

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    # 为了确保任何失败的数据库会话不会干扰模板触发的其他数据库访问
    # 执行会话回滚来将会话重置为干净的状态
    db.session.rollback()
    return render_template('500.html'), 500