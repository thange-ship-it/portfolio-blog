import markdown
from flask import Blueprint, render_template, abort

from app.models import BlogPost

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def blog_list():
    posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).all()
    return render_template('blog/list.html', posts=posts)


@blog_bp.route('/<slug>')
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    content_html = markdown.markdown(post.content, extensions=['fenced_code', 'codehilite', 'tables'])
    return render_template('blog/post.html', post=post, content_html=content_html)
