import re
import markdown
from markupsafe import Markup
from flask import Blueprint, render_template, abort

from app.models import BlogPost

blog_bp = Blueprint('blog', __name__)


def content_preview(md_text, max_chars=200):
    """Convert Markdown to plain text and truncate for preview."""
    html = markdown.markdown(md_text)
    text = re.sub(r'<[^>]+>', '', html).strip()
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars].rsplit(' ', 1)[0]
    return truncated + '...'


@blog_bp.route('/')
def blog_list():
    posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).all()
    previews = {post.id: content_preview(post.content) for post in posts}
    return render_template('blog/list.html', posts=posts, previews=previews)


@blog_bp.route('/<slug>')
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    content_html = markdown.markdown(post.content, extensions=['fenced_code', 'codehilite', 'tables'])
    return render_template('blog/post.html', post=post, content_html=content_html)
