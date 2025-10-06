from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask_socketio import SocketIO, emit
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
socketio = SocketIO(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    edited_at = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    school_id = db.Column(db.String(50), nullable=True)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    edited_at = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def edit(self, new_content):
        self.content = new_content
        self.edited_at = datetime.datetime.utcnow()

    def delete(self):
        self.is_deleted = True

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(100), nullable=False)
    artist_name = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('requests', lazy=True))

class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip_address = db.Column(db.String(100))
    user_agent = db.Column(db.String(300))
    accessed_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref=db.backref('access_logs', lazy=True))


def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@app.before_request
def log_access():
    user_id = session.get('user_id')
    if user_id and request.endpoint not in ('static',):
        user = User.query.get(user_id)
        if user and user.username == 'admin':
            return
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        ua = request.headers.get('User-Agent')
        log = AccessLog(user_id=user_id, ip_address=ip, user_agent=ua)
        db.session.add(log)
        db.session.commit()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if not username or not password:
            flash("ユーザー名とパスワードを入力してください。", "danger")
            return redirect(url_for('register'))

        try:
            new_user = User(username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash("ユーザー登録が成功しました！", "success")
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash("そのユーザー名は既に使われています。", "danger")

    return render_template('login.html', action='登録', current_user=get_current_user())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("ログインしました！", "success")
            if not user.school_id:
                return redirect(url_for('input_school_id'))
            return redirect(url_for('request_form'))
        else:
            flash("ユーザー名またはパスワードが間違っています。", "danger")

    return render_template('login.html', action='ログイン', current_user=get_current_user())


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("ログアウトしました！", "success")
    return redirect(url_for('login'))


@app.route('/school_id', methods=['GET', 'POST'])
def input_school_id():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('login'))

    VALID_SCHOOL_ID = "hasaki3sousuke"

    if request.method == 'POST':
        school_id = request.form.get('school_id', '').strip()
        if not school_id:
            flash("学校IDを入力してください。", "danger")
        elif school_id != VALID_SCHOOL_ID:
            flash("この学校IDは間違っています。", "danger")
        else:
            current_user.school_id = school_id
            db.session.commit()
            flash("学校IDを保存しました。", "success")
            return redirect(url_for('request_form'))

    return render_template('school_id.html', current_user=current_user)


@app.route('/request', methods=['GET', 'POST'])
def request_form():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_request = Request(
            song_name=request.form['song_name'],
            artist_name=request.form['artist_name'],
            comment=request.form['comment'],
            user_id=current_user.id
        )
        db.session.add(new_request)
        db.session.commit()
        flash("リクエストが送信されました！", "success")
        return redirect(url_for('requests_list'))
    return render_template('request_form.html', current_user=current_user)


@app.route('/requests')
def requests_list():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('login'))
    requests = Request.query.all()
    return render_template('requests_list.html', requests=requests, current_user=current_user)


@app.route('/users')
def users_list():
    current_user = get_current_user()
    if not current_user or current_user.username != 'admin':
        flash("アクセス権限がありません。", "danger")
        return redirect(url_for('login'))
    users = User.query.all()
    return render_template('users_list.html', users=users, current_user=current_user)


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    current_user = get_current_user()
    if not current_user or current_user.username != 'admin':
        flash("アクセス権限がありません。", "danger")
        return redirect(url_for('login'))
    if current_user.id == user_id:
        flash("自分自身のアカウントは削除できません。", "warning")
        return redirect(url_for('users_list'))
    user_to_delete = User.query.get_or_404(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash(f"ユーザー {user_to_delete.username} を削除しました。", "success")
    return redirect(url_for('users_list'))


@app.route('/edit_message/<int:message_id>', methods=['POST'])
def edit_message(message_id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'ログインが必要です'}), 401

    message = ChatMessage.query.get_or_404(message_id)
    if message.user_id != current_user.id:
        return jsonify({'error': '他人のメッセージは編集できません'}), 403

    new_content = request.json.get('content', '').strip()
    if not new_content:
        return jsonify({'error': '内容が空です'}), 400

    message.content = new_content
    message.edited_at = datetime.datetime.utcnow()
    db.session.commit()

    socketio.emit('message_edited', {
        'message_id': message.id,
        'new_content': message.content,
        'edited_at': message.edited_at.strftime('%Y-%m-%d %H:%M:%S')
    }, broadcast=True)

    return jsonify({'success': True})


@app.route('/delete_message/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'ログインが必要です'}), 401

    message = ChatMessage.query.get_or_404(message_id)
    if message.user_id != current_user.id:
        return jsonify({'error': '他人のメッセージは削除できません'}), 403

    message.is_deleted = True
    db.session.commit()

    socketio.emit('message_deleted', {'message_id': message.id}, broadcast=True)
    return jsonify({'success': True})


@app.route('/chat')
def chat():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('login'))
    return render_template('chat.html', current_user=current_user)

@app.route('/get_messages')
def get_messages():
    messages = ChatMessage.query.order_by(ChatMessage.timestamp).all()
    result = [
        {
            'id': m.id,
            'username': m.username,
            'message': m.content,
            'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'edited_at': m.edited_at.strftime('%Y-%m-%d %H:%M:%S') if m.edited_at else None,
            'is_deleted': m.is_deleted,
            'user_id': m.user_id
        }
        for m in messages
    ]
    return jsonify(result)

@socketio.on('send_message')
def handle_send_message(data):
    current_user = get_current_user()
    if not current_user:
        return
    username = current_user.username
    message = data.get('message')
    if message:
        chat_msg = ChatMessage(username=username, content=message, user_id=current_user.id)
        db.session.add(chat_msg)
        db.session.commit()
        timestamp_str = chat_msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        emit('receive_message', {
            'message_id': chat_msg.id,
            'username': username,
            'message': message,
            'timestamp': timestamp_str,
            'user_id': current_user.id
        }, broadcast=True)


@app.route('/delete_request/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    current_user = get_current_user()
    if not current_user or current_user.username != 'admin':
        flash("この操作は許可されていません。", "danger")
        return redirect(url_for('requests_list'))
    request_to_delete = Request.query.get_or_404(request_id)
    db.session.delete(request_to_delete)
    db.session.commit()
    flash("リクエストを削除しました。", "success")
    return redirect(url_for('requests_list'))


@app.route('/change_credentials', methods=['GET', 'POST'])
def change_credentials():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_username = request.form['new_username'].strip()
        current_password = request.form['current_password'].strip()
        new_password = request.form['new_password'].strip()
        if not check_password_hash(current_user.password, current_password):
            flash('現在のパスワードが間違っています。', 'danger')
        else:
            if new_username and new_username != current_user.username:
                if User.query.filter_by(username=new_username).first():
                    flash('そのユーザー名はすでに使用されています。', 'danger')
                    return render_template('change_credentials.html', current_user=current_user)
                current_user.username = new_username
            if new_password:
                current_user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('ユーザー情報を変更しました。', 'success')
            return redirect(url_for('request_form'))
    return render_template('change_credentials.html', current_user=current_user)


@app.route('/access_logs', methods=['GET', 'POST'])
def access_logs():
    current_user = get_current_user()
    if not current_user or current_user.username != 'admin':
        flash("アクセス権限がありません。", "danger")
        return redirect(url_for('login'))
    if request.method == 'POST':
        command = request.form.get('command', '').strip().lower()
        if command == 'clear':
            AccessLog.query.delete()
            db.session.commit()
            flash("アクセスログをクリアしました。", "success")
            return redirect(url_for('access_logs'))
        else:
            flash(f"不明なコマンド: {command}", "warning")
    logs = AccessLog.query.order_by(AccessLog.accessed_at.desc()).all()
    return render_template('access_logs.html', logs=logs, current_user=current_user)


@socketio.on('admin_command')
def handle_admin_command(data):
    command = data.get('command')
    if command == 'clear':
        Message.query.delete()
        db.session.commit()
        socketio.emit('clear_all_messages')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='192.168.3.25', port=3000, debug=True)
