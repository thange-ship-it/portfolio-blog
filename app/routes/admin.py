from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import User, BlogPost

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password.', 'error')

    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@admin_bp.route('/')
@login_required
def dashboard():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/dashboard.html', posts=posts)


@admin_bp.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '')
        summary = request.form.get('summary', '').strip()
        published = request.form.get('published') == 'on'
        slug = BlogPost.generate_slug(title)

        # Ensure unique slug
        existing = BlogPost.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{BlogPost.query.count() + 1}"

        post = BlogPost(
            title=title,
            slug=slug,
            content=content,
            summary=summary,
            published=published
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/editor.html', post=None)


@admin_bp.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form.get('title', '').strip()
        post.content = request.form.get('content', '')
        post.summary = request.form.get('summary', '').strip()
        post.published = request.form.get('published') == 'on'

        new_slug = BlogPost.generate_slug(post.title)
        if new_slug != post.slug:
            existing = BlogPost.query.filter_by(slug=new_slug).first()
            if not existing:
                post.slug = new_slug

        db.session.commit()
        flash('Post updated successfully.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/editor.html', post=post)


@admin_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect(url_for('admin.dashboard'))
