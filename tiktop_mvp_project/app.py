from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Post
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tiktop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

# Inisialisasi database
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        
        # Validasi input
        if not username or not email or not password:
            flash('Semua bidang wajib diisi', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Kata laluan tidak sepadan', 'error')
            return render_template('register.html')
        
        # Periksa jika pengguna sudah wujud
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Nama pengguna sudah digunakan', 'error')
            return render_template('register.html')
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('E-mel sudah digunakan', 'error')
            return render_template('register.html')
        
        # Buat pengguna baru
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        # Simpan ke database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Pendaftaran berjaya! Sila log masuk', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Cari pengguna dalam database
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        
        if user and user.check_password(password):
            # Simpan ID pengguna dalam sesi
            session['user_id'] = user.id
            flash('Log masuk berjaya!', 'success')
            return redirect(url_for('feed'))
        else:
            flash('Nama pengguna atau kata laluan tidak sah', 'error')
    
    return render_template('login.html')

@app.route('/feed', methods=['GET', 'POST'])
def feed():
    # Periksa jika pengguna sudah log masuk
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Proses form posting baru
    if request.method == 'POST':
        content = request.form['content']
        if content and len(content) <= 200:
            new_post = Post(content=content, user_id=user.id)
            db.session.add(new_post)
            db.session.commit()
            flash('Post berhasil dibuat!', 'success')
        else:
            flash('Post tidak boleh kosong dan maksimum 200 aksara', 'error')
    
    # Ambil semua post untuk ditampilkan di feed
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('feed.html', username=user.username, posts=posts)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

# Buat database jika belum wujud
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)