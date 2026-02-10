from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/projects')
def projects():
    return render_template('projects.html')


@main_bp.route('/instructional-design')
def instructional_design():
    return render_template('instructional_design.html')
