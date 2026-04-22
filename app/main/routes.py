from flask import render_template, url_for, redirect, flash
from flask_login import login_required, current_user
from app.main import main
from app.models import Project, Certificate, Achievement

@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html', title='首页')

@main.route('/resume')
@login_required
def resume():
    return render_template('resume.html', title='个人简历')

@main.route('/projects')
@login_required
def projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', title='项目展示', projects=projects)

@main.route('/certificates')
@login_required
def certificates():
    certificates = Certificate.query.order_by(Certificate.issue_date.desc()).all()
    return render_template('certificates.html', title='证书展示', certificates=certificates)

@main.route('/achievements')
@login_required
def achievements():
    achievements = Achievement.query.order_by(Achievement.date.desc()).all()
    return render_template('achievements.html', title='成果展示', achievements=achievements)
