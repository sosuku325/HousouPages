# READMEはhatGPTに作らせたから間違いあるかもしれない。

# 📝 Description / 説明
As a member of the school broadcasting committee, I developed this web application to make it easy for students to send song requests online.  
放送委員として、生徒が簡単に楽曲リクエストを送信できるようにするために、このWebアプリを開発しました。


# 🎵 Flask Chat & Song Request App

> 🇬🇧 English version below | 🇯🇵 日本語版は下にあります

---

## 🇯🇵 日本語版

リアルタイムチャット機能付きの **Flask 製 Web アプリケーション** です。  
ユーザー登録、ログイン、学校ID認証、楽曲リクエスト投稿、アクセスログ、管理者専用機能などを備えています。

---

### 🚀 主な機能

| 機能 | 説明 |
|------|------|
| 🔐 **ユーザー認証** | 登録・ログイン・ログアウト。パスワードは安全にハッシュ化して保存。 |
| 🏫 **学校ID認証** | 有効な学校IDを入力しないと機能を利用できません。 |
| 💬 **リアルタイムチャット** | Flask-SocketIOによるリアルタイム通信。メッセージの編集・削除対応。 |
| 🎶 **リクエスト投稿** | 曲名・アーティスト名・コメントを登録可能。 |
| 👑 **管理者専用ページ** | ユーザー削除・リクエスト削除・アクセスログ閲覧／クリア機能。 |
| 🧾 **アクセスログ記録** | IP・User-Agent・アクセス日時を自動記録。 |
| ⚙️ **ユーザー情報変更** | ユーザー名やパスワードを変更可能。 |

---

### 🧩 使用技術

- **Backend:** Flask, Flask-SocketIO, SQLAlchemy  
- **Database:** SQLite  
- **Frontend:** Jinja2 Templates (HTML / CSS / JS)  
- **Auth:** Werkzeug Security (Password Hashing)

---


### ⚙️ セットアップ手順

#### 1️⃣ 環境構築

```bash
git clone https://github.com/sosuku325/HousouPages.git
cd HousouPages
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

#### 2️⃣ 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

> **requirements.txt 例**
> ```
> Flask
> Flask-SocketIO
> Flask-SQLAlchemy
> Werkzeug
> eventlet
> ```

#### 3️⃣ データベース初期化

```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

#### 4️⃣ アプリ起動

```bash
python app.py
```

🌐 デフォルトアクセス先: [http://192.168.3.25:3000](http://192.168.3.25:3000)

---

### 👑 管理者ユーザー

1. 通常通りユーザー登録  
2. `database.db` を開いて該当ユーザーの `username` を `"admin"` に変更  
3. 管理者専用ページにアクセス可能になります  

| ページ | URL |
|--------|------|
| ユーザー一覧 | `/users` |
| アクセスログ | `/access_logs` |
| リクエスト削除 | `/delete_request/<id>` |

---

### 🔒 学校ID認証

初回ログイン時に以下のIDを入力する必要があります：

```
hasaki3sousuke
```

変更する場合は、`app.py` 内の以下を修正してください：

```python
VALID_SCHOOL_ID = "hasaki3sousuke"
```

---

### ⚠️ 注意事項

- Flask-SocketIOを使用するため、`eventlet` のインストールが必要です。  
- SQLiteは軽量用途向けです。運用環境ではPostgreSQLなどを推奨します。  
- `SECRET_KEY` は本番環境で必ず変更してください。  

---

### 📜 ライセンス

このプロジェクトは [MIT License](LICENSE.md) の下で公開されています。  
© 2025 sosuku325

---

### 👤 作者

**sosuku325**  
GitHub: [@sosuku325](https://github.com/sosuku325)

---

---

## 🇬🇧 English Version

A **Flask-based web application** featuring real-time chat, user authentication, song request submission, access logs, and an admin panel.

---

### 🚀 Features

| Feature | Description |
|----------|-------------|
| 🔐 **User Authentication** | Register, login, and logout with secure password hashing |
| 🏫 **School ID Verification** | Users must input a valid school ID before using the app |
| 💬 **Real-Time Chat** | Powered by Flask-SocketIO with message edit/delete support |
| 🎶 **Song Requests** | Submit song title, artist name, and comment |
| 👑 **Admin Panel** | Manage users, delete requests, and view/clear access logs |
| 🧾 **Access Logging** | Records IP address, User-Agent, and access time |
| ⚙️ **Profile Management** | Change username and password easily |

---

### 🧩 Tech Stack

- **Backend:** Flask, Flask-SocketIO, SQLAlchemy  
- **Database:** SQLite  
- **Frontend:** Jinja2 Templates (HTML / CSS / JS)  
- **Auth:** Werkzeug Security (Password Hashing)

---


### ⚙️ Setup & Run

#### 1️⃣ Environment Setup

```bash
git clone https://github.com/sosuku325/HousouPages.git
cd HousouPages
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

#### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

> Example `requirements.txt`  
> ```
> Flask
> Flask-SocketIO
> Flask-SQLAlchemy
> Werkzeug
> eventlet
> ```

#### 3️⃣ Initialize Database

```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

#### 4️⃣ Run the App

```bash
python app.py
```

App runs at:  
🌐 **http://192.168.3.25:3000**

---

### 👑 Admin Account

To enable admin privileges:

1. Register a normal user  
2. Open `database.db`  
3. Change the `username` field to `"admin"`  

| Page | URL |
|------|------|
| Users List | `/users` |
| Access Logs | `/access_logs` |
| Delete Request | `/delete_request/<id>` |

---

### 🔒 School ID

You must enter the following ID on first login:

```
hasaki3sousuke
```

Change it by editing in `app.py`:

```python
VALID_SCHOOL_ID = "hasaki3sousuke"
```

---

### ⚠️ Notes

- Requires `eventlet` for WebSocket support.  
- SQLite is fine for testing but use PostgreSQL in production.  
- Change `SECRET_KEY` before deployment.  

---

### 📜 License

This project is released under the [MIT License](LICENSE.md).  
© 2025 sosuku325

---

### 👤 Author

**sosuku325**  
GitHub: [@sosuku325](https://github.com/sosuku325)

---

