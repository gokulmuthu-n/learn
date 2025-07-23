from flask import Flask, render_template, request, redirect, url_for, abort, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///model.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('post_id', 'username', name='_post_user_uc'),)

def init_db():
    if not os.path.exists('model.db'):
        with app.app_context():
            db.create_all()


init_db()

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            return render_template('login.html', error='Username required')
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts, username=session['username'])

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    return render_template('post_detail.html', post=post, comments=comments, username=session['username'])

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = session['username']
        content = request.form.get('content')
        if not content:
            return render_template('create_post.html', error='Content required', username=username)
        post = Post(username=username, content=content)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_post.html', username=session['username'])

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    post = Post.query.get_or_404(post_id)
    username = session['username']
    if username != post.username:
        abort(403)
    if request.method == 'POST':
        content = request.form.get('content')
        post.content = content
        post.last_updated = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('post_detail', post_id=post.id))
    return render_template('edit_post.html', post=post, username=username)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    post = Post.query.get_or_404(post_id)
    username = session['username']
    if username != post.username:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    post = Post.query.get_or_404(post_id)
    username = session['username']
    content = request.form.get('content')
    if not content:
        return redirect(url_for('post_detail', post_id=post_id))
    comment = Comment(post_id=post_id, username=username, content=content)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    comment = Comment.query.get_or_404(comment_id)
    username = session['username']
    if username != comment.username:
        abort(403)
    if request.method == 'POST':
        content = request.form.get('content')
        comment.content = content
        comment.last_updated = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('post_detail', post_id=comment.post_id))
    return render_template('edit_comment.html', comment=comment, username=username)

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    comment = Comment.query.get_or_404(comment_id)
    username = session['username']
    if username != comment.username:
        abort(403)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/post/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    post = Post.query.get_or_404(post_id)
    username = session['username']
    like = Like(post_id=post_id, username=username)
    db.session.add(like)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/post/<int:post_id>/unlike', methods=['POST'])
def unlike_post(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    post = Post.query.get_or_404(post_id)
    username = session['username']
    like = Like.query.filter_by(post_id=post_id, username=username).first()
    if like:
        db.session.delete(like)
        db.session.commit()
    return redirect(url_for('post_detail', post_id=post_id))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)

