from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.auth import auth
from app import db
from app.models import User

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            user = User.query.filter_by(username=username).first()
            
            if user:
                if user.check_password(password):
                    login_user(user)
                    next_page = request.args.get('next')
                    return redirect(next_page or url_for('main.home'))
                else:
                    flash('密码错误', 'danger')
            else:
                flash('用户不存在', 'danger')
        except Exception as e:
            flash(f'登录时发生错误: {str(e)}', 'danger')
    
    return render_template('login.html', title='登录')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        confirm_password = request.form.get('confirm_password') or ''

        if len(username) < 3:
            flash('用户名至少需要 3 个字符', 'danger')
            return render_template('register.html', title='注册')
        if len(password) < 6:
            flash('密码至少需要 6 个字符', 'danger')
            return render_template('register.html', title='注册')
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return render_template('register.html', title='注册')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('用户名已存在，请更换用户名', 'danger')
            return render_template('register.html', title='注册')

        try:
            user = User(username=username, is_admin=False)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash('注册成功，欢迎使用！', 'success')
            return redirect(url_for('main.permission_center'))
        except Exception as e:
            db.session.rollback()
            flash(f'注册失败: {str(e)}', 'danger')

    return render_template('register.html', title='注册')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))
