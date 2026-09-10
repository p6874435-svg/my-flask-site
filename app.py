from flask import Flask, request, render_template_string, jsonify, session, redirect, url_for
from functools import wraps
import sqlite3
from datetime import datetime
import random
import requests

app = Flask(__name__)
app.secret_key = 'super-secret-key-change-me-12345'

ADMIN_USER = 'admin'
ADMIN_PASS = 'daniil2026'

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated
# ===== TELEGRAM =====
BOT_TOKEN = "8802002179:AAF5ImK4UBwWyUb9hAAYuVNxSRY-_yMp7m8"
USER_ID = "@Ponomera2"

def send_telegram(name, phone, message):
    if BOT_TOKEN == "ТВОЙ_ТОКЕН_СЮДА":
        return
    try:
        text = f"📩 НОВАЯ ЗАЯВКА\n\nИмя: {name}\nТелефон: {phone}\nСообщение: {message}"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": USER_ID, "text": text})
    except:
        pass

# ===== БАЗА ДАННЫХ =====
def init_db():
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT, message TEXT, created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, content TEXT, created_at TEXT
    )''')
    conn.commit()
    conn.close()

def add_message(name, phone, message):
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (name, phone, message, created_at) VALUES (?, ?, ?, ?)',
              (name, phone, message, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    conn.close()

def get_messages(search=""):
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    if search:
        c.execute("SELECT * FROM messages WHERE name LIKE ? OR phone LIKE ? OR message LIKE ? ORDER BY id DESC",
                  (f'%{search}%', f'%{search}%', f'%{search}%'))
    else:
        c.execute('SELECT * FROM messages ORDER BY id DESC')
    return c.fetchall()

def get_count():
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM messages')
    count = c.fetchone()[0]
    conn.close()
    return count

def delete_message(msg_id):
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    c.execute('DELETE FROM messages WHERE id = ?', (msg_id,))
    conn.commit()
    conn.close()

def add_post(title, content):
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    c.execute('INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)',
              (title, content, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    conn.close()

def get_posts():
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    c.execute('SELECT * FROM posts ORDER BY id DESC')
    return c.fetchall()

init_db()

# ===== HTML СТРАНИЦЫ =====
MAIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Даниил — Веб-разработчик</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
/* ===== ЦВЕТОВЫЕ ТЕМЫ ===== */
:root {
    --bg: #0b0f1a;
    --bg2: rgba(255,255,255,0.05);
    --card: rgba(255,255,255,0.05);
    --text: #ffffff;
    --text2: #aaa;
    --border: rgba(255,255,255,0.08);
    --accent: #6c63ff;
    --accent2: #ff6b6b;
    --nav: rgba(11,15,26,0.7);
}

body.theme-light {
    --bg: #f0f4ff;
    --bg2: rgba(108,99,255,0.05);
    --card: #ffffff;
    --text: #1a1a2e;
    --text2: #6b7280;
    --border: rgba(0,0,0,0.08);
    --accent: #6c63ff;
    --accent2: #ff6b6b;
    --nav: rgba(255,255,255,0.8);
}

body.theme-gold {
    --bg: #0a0a0a;
    --bg2: rgba(212,175,55,0.05);
    --card: rgba(212,175,55,0.05);
    --text: #f5f5f5;
    --text2: #a08c4d;
    --border: rgba(212,175,55,0.15);
    --accent: #d4af37;
    --accent2: #b8941f;
    --nav: rgba(10,10,10,0.8);
}

body.theme-ocean {
    --bg: #0a1929;
    --bg2: rgba(0,212,255,0.05);
    --card: rgba(0,212,255,0.05);
    --text: #e3f2fd;
    --text2: #64b5f6;
    --border: rgba(0,212,255,0.15);
    --accent: #00d4ff;
    --accent2: #0095d4;
    --nav: rgba(10,25,41,0.8);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Segoe UI', Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    transition: background 0.5s, color 0.5s;
    overflow-x: hidden;
    position: relative;
}
body::before {
    content: '';
    position: fixed;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at 20% 30%, var(--accent) 0%, transparent 40%),
                radial-gradient(circle at 80% 70%, var(--accent2) 0%, transparent 40%);
    opacity: 0.12;
    animation: floatBg 20s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
    transition: opacity 0.5s;
}
@keyframes floatBg {
    0%, 100% { transform: translate(0,0) rotate(0deg); }
    50% { transform: translate(-5%,-5%) rotate(10deg); }
}

header {
    position: relative;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    padding: 100px 20px;
    text-align: center;
    overflow: hidden;
    animation: slideDown 1s ease;
    transition: background 0.5s;
}
header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="1" fill="white" opacity="0.3"/><circle cx="80" cy="40" r="1.5" fill="white" opacity="0.4"/><circle cx="40" cy="80" r="1" fill="white" opacity="0.3"/></svg>');
    background-size: 400px;
    animation: starMove 40s linear infinite;
}
@keyframes starMove { from { background-position: 0 0; } to { background-position: 400px 400px; } }
header h1 { font-size: 68px; letter-spacing: 2px; position: relative; z-index: 1; color: #fff; }
header p { font-size: 22px; opacity: 0.95; margin-top: 10px; position: relative; z-index: 1; color: #fff; }

@keyframes slideDown { from { transform: translateY(-100px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
@keyframes fadeUp { from { transform: translateY(50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
@keyframes shine { 0% { background-position: -200% center; } 100% { background-position: 200% center; } }

nav {
    background: var(--nav);
    backdrop-filter: blur(20px);
    padding: 18px;
    text-align: center;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 100;
    transition: background 0.5s;
}
nav a { color: var(--text2); text-decoration: none; font-weight: 600; font-size: 15px; transition: 0.3s; padding: 8px 16px; border-radius: 30px; }
nav a:hover { color: var(--accent); background: rgba(108,99,255,0.15); transform: translateY(-2px); }

/* ПЕРЕКЛЮЧАТЕЛЬ ТЕМ */
.theme-switcher {
    display: flex;
    gap: 6px;
    background: var(--card);
    border: 1px solid var(--border);
    padding: 5px;
    border-radius: 30px;
}
.theme-btn {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 2px solid transparent;
    cursor: pointer;
    transition: 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}
.theme-btn:hover { transform: scale(1.15); }
.theme-btn.active { border-color: var(--accent); box-shadow: 0 0 15px var(--accent); }
.theme-btn[data-theme="dark"] { background: linear-gradient(135deg, #0b0f1a, #6c63ff); }
.theme-btn[data-theme="light"] { background: linear-gradient(135deg, #fff, #6c63ff); }
.theme-btn[data-theme="gold"] { background: linear-gradient(135deg, #0a0a0a, #d4af37); }
.theme-btn[data-theme="ocean"] { background: linear-gradient(135deg, #0a1929, #00d4ff); }

.container { max-width: 1200px; margin: 50px auto; padding: 0 20px; position: relative; z-index: 1; animation: fadeUp 1s ease; }

.hero {
    background: linear-gradient(135deg, rgba(108,99,255,0.15), rgba(255,107,107,0.15));
    padding: 70px 60px;
    border-radius: 30px;
    text-align: center;
    border: 1px solid var(--border);
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%; right: -50%;
    width: 200%; height: 200%;
    background: conic-gradient(from 0deg, transparent, var(--accent), transparent 30%);
    opacity: 0.15;
    animation: rotate 8s linear infinite;
    pointer-events: none;
}
@keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.hero h2 {
    font-size: 48px;
    position: relative;
    z-index: 1;
    background: linear-gradient(90deg, var(--text) 0%, var(--accent) 50%, var(--text) 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 4s linear infinite;
}
.hero p { font-size: 20px; color: var(--text2); margin: 20px 0; position: relative; z-index: 1; }

.btn {
    display: inline-block;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: #fff;
    padding: 16px 48px;
    border-radius: 50px;
    text-decoration: none;
    font-weight: 700;
    font-size: 17px;
    transition: 0.3s;
    box-shadow: 0 10px 30px rgba(108,99,255,0.3);
    border: none;
    cursor: pointer;
    position: relative;
    z-index: 1;
    overflow: hidden;
}
.btn::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    transition: 0.6s;
}
.btn:hover::before { left: 100%; }
.btn:hover { transform: translateY(-3px) scale(1.05); }

.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 20px; margin: 50px 0; }
.stat {
    background: var(--card);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    border: 1px solid var(--border);
    backdrop-filter: blur(20px);
    transition: 0.4s;
}
.stat:hover { transform: translateY(-5px); border-color: var(--accent); }
.stat h2 {
    font-size: 42px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat p { color: var(--text2); }

.features { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 30px; margin-top: 50px; }
.feature {
    background: var(--card);
    padding: 40px 30px;
    border-radius: 25px;
    text-align: center;
    border: 1px solid var(--border);
    backdrop-filter: blur(20px);
    transition: 0.5s;
}
.feature:hover {
    transform: translateY(-10px) rotateX(5deg) rotateY(-5deg);
    border-color: var(--accent);
}
.feature i {
    font-size: 55px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 20px;
    display: block;
    transition: 0.4s;
}
.feature:hover i { transform: scale(1.2) rotate(-10deg); }
.feature h3 { font-size: 22px; margin-bottom: 10px; }
.feature p { color: var(--text2); }

.section-title {
    font-size: 38px;
    text-align: center;
    margin: 70px 0 30px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.pricing { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; }
.price-card {
    background: var(--card);
    padding: 40px 35px;
    border-radius: 25px;
    border: 1px solid var(--border);
    backdrop-filter: blur(20px);
    transition: 0.5s;
    position: relative;
}
.price-card:hover {
    transform: translateY(-15px);
    border-color: var(--accent);
}
.price-card.popular::before {
    content: '🔥 ПОПУЛЯРНЫЙ';
    position: absolute;
    top: -14px; left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, var(--accent2), var(--accent));
    padding: 6px 20px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
    color: #fff;
}
.price-card h3 { font-size: 24px; margin-bottom: 10px; }
.price-card .price {
    font-size: 48px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    margin: 15px 0;
}
.price-card ul { list-style: none; margin: 25px 0; }
.price-card li { padding: 10px 0; color: var(--text2); border-bottom: 1px solid var(--border); }
.price-card li:last-child { border-bottom: none; }
.price-card li i { color: #22c55e; margin-right: 10px; }

.gallery { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; }
.gallery-item {
    height: 200px;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font: 600 18px Georgia;
    color: #fff;
    text-align: center;
    padding: 20px;
    transition: 0.5s;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.gallery-item::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    transition: 0.6s;
}
.gallery-item:hover::before { left: 100%; }
.gallery-item:hover { transform: scale(1.08) rotate(2deg); }
.gallery-item:nth-child(1) { background: linear-gradient(135deg, #d8c0ad, #9d765e); }
.gallery-item:nth-child(2) { background: linear-gradient(135deg, #eaded4, #c3a28c); }
.gallery-item:nth-child(3) { background: linear-gradient(135deg, #cfc2b4, #8f8173); }
.gallery-item:nth-child(4) { background: linear-gradient(135deg, #e8ddd5, #bda18e); }

.blog-preview {
    background: var(--card);
    padding: 35px;
    border-radius: 25px;
    border: 1px solid var(--border);
    backdrop-filter: blur(20px);
    margin-top: 40px;
}
.blog-preview .post-item {
    border-bottom: 1px solid var(--border);
    padding: 18px 0;
    transition: 0.3s;
}
.blog-preview .post-item:hover { padding-left: 15px; }
.blog-preview .post-item:last-child { border-bottom: none; }
.blog-preview .post-item a { color: var(--accent); text-decoration: none; font-weight: 600; font-size: 17px; }

footer {
    background: var(--bg2);
    text-align: center;
    padding: 40px;
    margin-top: 60px;
    border-top: 1px solid var(--border);
}
.footer-links a { color: var(--accent); margin: 0 15px; text-decoration: none; transition: 0.3s; }
.footer-links a:hover { color: var(--accent2); }

.reveal { opacity: 0; transform: translateY(40px); transition: 0.8s ease; }
.reveal.active { opacity: 1; transform: translateY(0); }

@media (max-width: 768px) {
    header h1 { font-size: 40px; }
    .hero h2 { font-size: 30px; }
    .hero { padding: 40px 25px; }
}
</style>
</head>
<body class="theme-dark">
<header>
    <h1>🚀 Даниил</h1>
    <p>Веб-разработчик на Python</p>
</header>
<nav>
    <a href="/">Главная</a>
    <a href="/portfolio">Портфолио</a>
    <a href="/pricing">Цены</a>
    <a href="/blog">Блог</a>
    <a href="/contact">Контакты</a>
    <a href="/admin">Админ</a>
    <a href="/chat">Чат-бот</a>
    <div class="theme-switcher">
        <button class="theme-btn active" data-theme="dark" onclick="setTheme('dark')" title="Тёмная">🌙</button>
        <button class="theme-btn" data-theme="light" onclick="setTheme('light')" title="Светлая">☀️</button>
        <button class="theme-btn" data-theme="gold" onclick="setTheme('gold')" title="Золотая">👑</button>
        <button class="theme-btn" data-theme="ocean" onclick="setTheme('ocean')" title="Океан">🌊</button>
    </div>
</nav>
<div class="container">
    <div class="hero reveal">
        <h2>🔥 Создаю сайты, которые работают</h2>
        <p>Современные сайты, Telegram-боты и веб-приложения на Python</p>
        <a href="/contact" class="btn">Связаться</a>
    </div>

    <div class="stats reveal">
        <div class="stat"><h2 data-count="4">0</h2><p>Проектов</p></div>
        <div class="stat"><h2 data-count="{{ count }}">{{ count }}</h2><p>Заявок</p></div>
        <div class="stat"><h2 data-count="100">0</h2><p>% на Python</p></div>
        <div class="stat"><h2>24/7</h2><p>На связи</p></div>
    </div>

    <div class="features reveal">
        <div class="feature"><i class="fas fa-code"></i><h3>Сайты на Python</h3><p>Современные сайты с админкой и БД</p></div>
        <div class="feature"><i class="fas fa-robot"></i><h3>Telegram-боты</h3><p>Автоматизация продаж</p></div>
        <div class="feature"><i class="fas fa-database"></i><h3>Веб-приложения</h3><p>CRM, кабинеты, дашборды</p></div>
        <div class="feature"><i class="fas fa-palette"></i><h3>Дизайн</h3><p>Анимации, градиенты</p></div>
    </div>

    <h2 class="section-title reveal">💰 Мои цены</h2>
    <div class="pricing reveal">
        <div class="price-card">
            <h3>Лендинг</h3>
            <div class="price">5 000 ₽</div>
            <ul><li><i class="fas fa-check"></i>Одностраничный сайт</li><li><i class="fas fa-check"></i>Адаптивный дизайн</li><li><i class="fas fa-check"></i>Форма заявки</li></ul>
            <a href="/contact" class="btn" style="width:100%;text-align:center">Заказать</a>
        </div>
        <div class="price-card popular">
            <h3>Сайт + Админка</h3>
            <div class="price">15 000 ₽</div>
            <ul><li><i class="fas fa-check"></i>Многостраничный</li><li><i class="fas fa-check"></i>Админ-панель</li><li><i class="fas fa-check"></i>База данных</li></ul>
            <a href="/contact" class="btn" style="width:100%;text-align:center">Заказать</a>
        </div>
        <div class="price-card">
            <h3>Сайт + Бот</h3>
            <div class="price">25 000 ₽</div>
            <ul><li><i class="fas fa-check"></i>Всё из «+ Админка»</li><li><i class="fas fa-check"></i>Telegram-бот</li><li><i class="fas fa-check"></i>Уведомления</li></ul>
            <a href="/contact" class="btn" style="width:100%;text-align:center">Заказать</a>
        </div>
    </div>

    <h2 class="section-title reveal">📸 Мои работы</h2>
    <div class="gallery reveal">
        <div class="gallery-item">SPA STUDIO<br>Евгения</div>
        <div class="gallery-item">DR. MANIFIK<br>Minimal</div>
        <div class="gallery-item">DR. MANIFIK<br>Premium</div>
        <div class="gallery-item">IRINA<br>Косметолог</div>
    </div>

    <div class="blog-preview reveal">
        <h3 style="margin-bottom:20px">📝 Блог</h3>
        {% for post in posts %}
        <div class="post-item">
            <a href="/post/{{ post[0] }}">{{ post[1] }}</a>
            <small style="color:var(--text2);margin-left:15px">{{ post[3] }}</small>
        </div>
        {% endfor %}
        {% if posts|length == 0 %}<p style="color:var(--text2)">Нет записей</p>{% endif %}
    </div>
</div>
<footer>
    <p>&copy; 2026 Даниил — Веб-разработчик</p>
    <div class="footer-links" style="margin-top:15px">
        <a href="/">Главная</a>
        <a href="/portfolio">Портфолио</a>
        <a href="/pricing">Цены</a>
        <a href="/blog">Блог</a>
        <a href="/contact">Контакты</a>
        <a href="/admin">Админ</a>
    </div>
</footer>
<script>
// Управление темами
function setTheme(theme) {
    document.body.className = 'theme-' + theme;
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === theme);
    });
    localStorage.setItem('site-theme', theme);
}

// Загружаем тему при загрузке
const savedTheme = localStorage.getItem('site-theme') || 'dark';
setTheme(savedTheme);

// Анимация появления при скролле
const reveals = document.querySelectorAll('.reveal');
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('active');
            const counters = entry.target.querySelectorAll('[data-count]');
            counters.forEach(counter => {
                const target = +counter.dataset.count;
                let current = 0;
                const step = Math.max(1, Math.floor(target / 40));
                const timer = setInterval(() => {
                    current += step;
                    if (current >= target) { current = target; clearInterval(timer); }
                    counter.textContent = current + (counter.textContent.includes('%') ? '%' : '');
                }, 30);
            });
        }
    });
}, { threshold: 0.15 });
reveals.forEach(el => observer.observe(el));
</script>
</body>
</html>
'''

ABOUT_HTML = '''<!DOCTYPE html><html><head><title>О нас</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Segoe UI,Arial,sans-serif;background:#0b0f1a;color:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px}.card{background:rgba(255,255,255,0.05);border-radius:30px;border:1px solid rgba(255,255,255,0.08);max-width:700px;width:100%;padding:50px;text-align:center}.avatar i{font-size:100px;color:#6c63ff;background:rgba(108,99,255,0.15);padding:30px;border-radius:50%}h1{font-size:36px;margin:20px 0 10px}.subtitle{color:#6c63ff;font-size:18px}.bio{color:#aaa;line-height:1.8;margin:20px 0}.btn{display:inline-block;background:#6c63ff;color:#fff;padding:12px 30px;border-radius:50px;text-decoration:none;font-weight:600;margin-top:20px}</style></head><body><div class="card"><div class="avatar"><i class="fas fa-user-astronaut"></i></div><h1>👋 Привет, я Даниил!</h1><p class="subtitle">Веб-разработчик на Python</p><div class="bio">Создаю сайты, Telegram-ботов и веб-приложения. Люблю учиться новому и решать сложные задачи.</div><a href="/" class="btn">На главную</a></div></body></html>'''

PORTFOLIO_HTML = '''<!DOCTYPE html><html><head><title>Портфолио</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0f1a;color:#fff;font-family:Segoe UI,Arial,sans-serif;padding:40px 20px}.container{max-width:1100px;margin:0 auto}.card{background:rgba(255,255,255,0.05);padding:40px;border-radius:25px;border:1px solid rgba(255,255,255,0.08)}h1{text-align:center;font-size:42px;margin-bottom:15px}.sub{text-align:center;color:#aaa;margin-bottom:40px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:25px}.item{background:rgba(255,255,255,0.05);border-radius:20px;overflow:hidden;transition:0.3s;border:1px solid rgba(255,255,255,0.05)}.item:hover{transform:translateY(-10px);border-color:#6c63ff}.preview{height:200px;display:flex;align-items:center;justify-content:center;font:600 22px Georgia;color:#fff;letter-spacing:3px}.item:nth-child(1) .preview{background:linear-gradient(135deg,#d8c0ad,#9d765e)}.item:nth-child(2) .preview{background:linear-gradient(135deg,#eaded4,#c3a28c)}.item:nth-child(3) .preview{background:linear-gradient(135deg,#cfc2b4,#8f8173)}.item:nth-child(4) .preview{background:linear-gradient(135deg,#e8ddd5,#bda18e)}.info{padding:25px}.info h3{font-size:20px;margin-bottom:10px}.info p{color:#aaa;font-size:14px;margin-bottom:15px}.tags span{display:inline-block;background:rgba(108,99,255,0.15);color:#9d94ff;padding:5px 12px;border-radius:20px;font-size:12px;font-weight:600;margin-right:5px}a{color:#6c63ff;text-decoration:none;display:block;margin-top:20px;text-align:center}</style></head><body><div class="container"><div class="card"><h1>💼 Мои работы</h1><p class="sub">Демо-сайты, которые я сделал</p><div class="grid"><div class="item"><div class="preview">SPA STUDIO</div><div class="info"><h3>Студия Евгении</h3><p>Сайт студии SPA-массажа</p><div class="tags"><span>Сайт</span><span>SPA</span></div></div></div><div class="item"><div class="preview">MANIFIK</div><div class="info"><h3>Dr. Manifik — Minimal</h3><p>Клиника косметологии</p><div class="tags"><span>Сайт</span><span>Медицина</span></div></div></div><div class="item"><div class="preview">PREMIUM</div><div class="info"><h3>Dr. Manifik — Premium</h3><p>Премиум-версия сайта</p><div class="tags"><span>Сайт</span><span>Премиум</span></div></div></div><div class="item"><div class="preview">IRINA</div><div class="info"><h3>Ирина — косметолог</h3><p>Сайт косметолога из Ялты</p><div class="tags"><span>Сайт</span><span>Косметология</span></div></div></div></div><a href="/">← На главную</a></div></div></body></html>'''

PRICING_HTML = '''<!DOCTYPE html><html><head><title>Цены</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0f1a;color:#fff;font-family:Segoe UI,Arial,sans-serif;padding:40px 20px}.container{max-width:1100px;margin:0 auto;text-align:center}h1{font-size:42px;margin-bottom:15px}.sub{color:#aaa;margin-bottom:40px}.pricing{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:25px;text-align:left}.price-card{background:rgba(255,255,255,0.05);padding:35px;border-radius:25px;border:1px solid rgba(255,255,255,0.08);transition:0.4s;position:relative}.price-card:hover{transform:translateY(-10px);border-color:#6c63ff}.price-card.popular::before{content:'ПОПУЛЯРНЫЙ';position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:#ff6b6b;padding:4px 15px;border-radius:20px;font-size:11px;font-weight:700}.price-card h3{font-size:24px;margin-bottom:10px}.price-card .price{font-size:42px;color:#6c63ff;font-weight:700;margin:15px 0}.price-card ul{list-style:none;margin:20px 0}.price-card li{padding:8px 0;color:#ccc}.price-card li i{color:#22c55e;margin-right:10px}.btn{display:inline-block;background:linear-gradient(135deg,#6c63ff,#ff6b6b);color:#fff;padding:14px 30px;border-radius:50px;text-decoration:none;font-weight:700;width:100%;text-align:center;margin-top:15px}a{color:#6c63ff;text-decoration:none;display:block;margin-top:30px;text-align:center}</style></head><body><div class="container"><h1>💰 Цены</h1><p class="sub">Прозрачные цены без скрытых платежей</p><div class="pricing"><div class="price-card"><h3>Лендинг</h3><div class="price">5 000 ₽</div><ul><li><i class="fas fa-check"></i>Одностраничный сайт</li><li><i class="fas fa-check"></i>Адаптивный дизайн</li><li><i class="fas fa-check"></i>Форма заявки</li></ul><a href="/contact" class="btn">Заказать</a></div><div class="price-card popular"><h3>Сайт + Админка</h3><div class="price">15 000 ₽</div><ul><li><i class="fas fa-check"></i>Многостраничный</li><li><i class="fas fa-check"></i>Админ-панель</li><li><i class="fas fa-check"></i>База данных</li></ul><a href="/contact" class="btn">Заказать</a></div><div class="price-card"><h3>Сайт + Бот</h3><div class="price">25 000 ₽</div><ul><li><i class="fas fa-check"></i>Всё из «+ Админка»</li><li><i class="fas fa-check"></i>Telegram-бот</li><li><i class="fas fa-check"></i>Уведомления</li></ul><a href="/contact" class="btn">Заказать</a></div></div><a href="/">← На главную</a></div></body></html>'''

BLOG_HTML = '''<!DOCTYPE html><html><head><title>Блог</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0f1a;color:#fff;font-family:Segoe UI,Arial,sans-serif;padding:40px 20px}.container{max-width:900px;margin:0 auto}.card{background:rgba(255,255,255,0.05);padding:40px;border-radius:25px;border:1px solid rgba(255,255,255,0.08)}h1{text-align:center}.post{border-bottom:1px solid rgba(255,255,255,0.06);padding:20px 0}.post:last-child{border-bottom:none}.post small{color:#666}.post p{color:#aaa}a{color:#6c63ff;text-decoration:none;display:block;margin-top:20px;text-align:center}</style></head><body><div class="container"><div class="card"><h1>📝 Блог</h1>{% for post in posts %}<div class="post"><h3>{{ post[1] }}</h3><small>{{ post[3] }}</small><p>{{ post[2][:200] }}...</p><a href="/post/{{ post[0] }}">Читать →</a></div>{% endfor %}{% if posts|length==0 %}<p>Нет записей</p>{% endif %}<a href="/">← На главную</a></div></div></body></html>'''

POST_HTML = '''<!DOCTYPE html><html><head><title>Статья</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0f1a;color:#fff;font-family:Segoe UI,Arial,sans-serif;padding:40px 20px}.container{max-width:800px;margin:0 auto}.card{background:rgba(255,255,255,0.05);padding:40px;border-radius:25px;border:1px solid rgba(255,255,255,0.08)}h1{color:#fff}small{color:#666;display:block;margin:10px 0}p{color:#aaa;line-height:1.8}.btn{display:inline-block;background:#6c63ff;color:#fff;padding:10px 25px;border-radius:20px;text-decoration:none;margin-top:20px}</style></head><body><div class="container"><div class="card"><h1>{{ post[1] }}</h1><small>{{ post[3] }}</small><p>{{ post[2] }}</p><a href="/blog" class="btn">Все записи</a></div></div></body></html>'''

CONTACT_HTML = '''<!DOCTYPE html><html><head><title>Контакты</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0f1a;color:#fff;font-family:Segoe UI,Arial,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px}.card{background:rgba(255,255,255,0.05);padding:40px;border-radius:30px;border:1px solid rgba(255,255,255,0.08);max-width:500px;width:100%}h1{text-align:center;margin-bottom:20px}h1 i{color:#6c63ff}input,textarea{width:100%;padding:14px;margin:10px 0;border-radius:12px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:#fff;font-size:16px}input:focus,textarea:focus{outline:none;border-color:#6c63ff}button{width:100%;padding:15px;border-radius:12px;border:none;background:linear-gradient(135deg,#6c63ff,#ff6b6b);color:#fff;font-size:18px;font-weight:600;cursor:pointer}a{color:#6c63ff;text-decoration:none;display:inline-block;margin-top:15px}</style></head><body><div class="card"><h1><i class="fas fa-paper-plane"></i> Напиши мне</h1><form method="POST"><input type="text" name="name" placeholder="Имя" required><input type="text" name="phone" placeholder="Телефон" required><textarea name="message" rows="5" placeholder="Сообщение" required></textarea><button type="submit">Отправить</button></form><a href="/">На главную</a></div></body></html>'''

SUCCESS_HTML = '''<!DOCTYPE html><html><head><title>Спасибо!</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0f1a;color:#fff;font-family:Segoe UI,Arial,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;padding:20px}.card{background:rgba(255,255,255,0.05);padding:50px;border-radius:30px;text-align:center;border:1px solid rgba(255,255,255,0.08);max-width:500px;width:100%}.card i{font-size:80px;color:#22c55e}h1{color:#fff}a{color:#6c63ff;text-decoration:none;font-weight:600}</style></head><body><div class="card"><i class="fas fa-check-circle"></i><h1>✅ Спасибо, {{ name }}!</h1><p>Ваша заявка принята.</p><br><a href="/">На главную</a></div></body></html>'''

ADMIN_HTML = '''<!DOCTYPE html><html><head><title>Админ-панель</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><script src="https://cdn.jsdelivr.net/npm/chart.js"></script><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0f1a;color:#fff;font-family:Segoe UI,Arial,sans-serif;padding:20px}.container{max-width:1200px;margin:0 auto;background:rgba(255,255,255,0.05);padding:30px;border-radius:25px;border:1px solid rgba(255,255,255,0.08)}h1{display:flex;align-items:center;gap:10px;margin-bottom:20px}h2{margin:25px 0 15px;color:#6c63ff}table{width:100%;border-collapse:collapse;margin-top:20px}th,td{padding:12px;border:1px solid rgba(255,255,255,0.08);text-align:left}th{background:linear-gradient(135deg,#6c63ff,#ff6b6b)}input,textarea{width:100%;padding:10px;margin:10px 0;border-radius:10px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:#fff}.btn{display:inline-block;background:#6c63ff;color:#fff;padding:12px 25px;border-radius:12px;text-decoration:none;margin-top:20px;border:none;cursor:pointer;transition:0.3s}.btn:hover{background:#4a42d4;transform:scale(1.05)}.search-box{display:flex;gap:10px;margin:20px 0}.search-box input{flex:1}.del-btn{color:#ff6b6b;text-decoration:none;font-size:18px}.chart-container{background:rgba(255,255,255,0.03);padding:25px;border-radius:20px;margin:25px 0;border:1px solid rgba(255,255,255,0.06)}</style></head><body><div class="container"><h1><i class="fas fa-cog"></i> Админ-панель <span style="background:#6c63ff;padding:5px 15px;border-radius:20px;font-size:14px">{{ count }} заявок</span></h1>

<div class="chart-container">
<h2 style="margin-top:0">📊 Статистика заявок</h2>
<canvas id="statsChart" height="80"></canvas>
</div>

<form method="GET" class="search-box"><input type="text" name="search" placeholder="🔍 Поиск по заявкам..." value="{{ search }}"><button type="submit" class="btn" style="margin:0">Найти</button></form>

<h2>📋 Заявки</h2>
<table><tr><th>ID</th><th>Имя</th><th>Телефон</th><th>Сообщение</th><th>Дата</th><th></th></tr>{% for msg in messages %}<tr><td>{{ msg[0] }}</td><td>{{ msg[1] }}</td><td>{{ msg[2] }}</td><td>{{ msg[3] }}</td><td>{{ msg[4] }}</td><td><a href="/admin/delete/{{ msg[0] }}" class="del-btn" onclick="return confirm('Удалить?')">🗑️</a></td></tr>{% endfor %}</table>

<h2>📝 Добавить запись в блог</h2>
<form method="POST" action="/admin/add_post"><input type="text" name="title" placeholder="Заголовок" required><textarea name="content" rows="5" placeholder="Текст" required></textarea><button type="submit" class="btn">Добавить</button></form>

<a href="/" class="btn">← На главную</a>
</div>
<script>
const ctx = document.getElementById('statsChart');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Пн','Вт','Ср','Чт','Пт','Сб','Вс'],
        datasets: [{
            label: 'Заявки за неделю',
            data: [2, 5, 3, 8, 4, 6, {{ count }}],
            borderColor: '#6c63ff',
            backgroundColor: 'rgba(108,99,255,0.15)',
            borderWidth: 3,
            tension: 0.4,
            fill: true,
            pointBackgroundColor: '#ff6b6b',
            pointRadius: 6
        }]
    },
    options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#fff' } } },
        scales: {
            y: { ticks: { color: '#aaa' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            x: { ticks: { color: '#aaa' }, grid: { color: 'rgba(255,255,255,0.05)' } }
        }
    }
});
</script>
</body></html>'''

CHAT_HTML = '''<!DOCTYPE html><html><head><title>Чат-бот</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0f1a;color:#fff;font-family:Segoe UI,Arial,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px}.chat-container{background:rgba(255,255,255,0.05);padding:30px;border-radius:30px;border:1px solid rgba(255,255,255,0.08);max-width:500px;width:100%}.chat-box{background:rgba(255,255,255,0.03);border-radius:15px;padding:15px;min-height:350px;max-height:400px;overflow-y:auto;margin-bottom:15px}.msg{padding:10px 15px;border-radius:15px;margin:5px 0;max-width:80%}.bot-msg{background:linear-gradient(135deg,#6c63ff,#4a42d4);color:#fff}.user-msg{background:rgba(255,255,255,0.1);color:#fff;margin-left:auto;text-align:right}.chat-input{display:flex;gap:10px}.chat-input input{flex:1;padding:12px;border-radius:25px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:#fff;font-size:16px}.chat-input button{padding:12px 22px;border-radius:25px;border:none;background:linear-gradient(135deg,#6c63ff,#4a42d4);color:#fff;cursor:pointer;font-size:18px}.quick{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;justify-content:center}.quick button{background:rgba(108,99,255,0.15);border:1px solid rgba(108,99,255,0.2);color:#ccc;padding:6px 14px;border-radius:20px;cursor:pointer;font-size:13px}a{color:#6c63ff;text-decoration:none;display:block;margin-top:15px;text-align:center}</style></head><body><div class="chat-container"><h1 style="text-align:center;margin-bottom:15px"><i class="fas fa-robot" style="color:#6c63ff"></i> Чат-бот</h1><div class="chat-box" id="chatBox"><div class="msg bot-msg">🤖 Привет! Задай мне вопрос!</div></div><div class="quick"><button onclick="sendQuick('Привет')">👋 Привет</button><button onclick="sendQuick('Расскажи шутку')">😂 Шутка</button><button onclick="sendQuick('Что такое Python?')">🐍 Python</button><button onclick="sendQuick('Помоги с кодом')">💻 Код</button><button onclick="sendQuick('Курс валют')">💰 Валюты</button></div><div class="chat-input" style="margin-top:12px"><input type="text" id="question" placeholder="Напиши вопрос..."><button onclick="sendMessage()"><i class="fas fa-paper-plane"></i></button></div><a href="/">На главную</a></div><script>
async function sendMessage(){const input=document.getElementById('question');const chatBox=document.getElementById('chatBox');const text=input.value.trim();if(!text)return;chatBox.innerHTML+=`<div class="msg user-msg">👤 ${text}</div>`;input.value='';chatBox.scrollTop=chatBox.scrollHeight;const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:text})});const d=await r.json();chatBox.innerHTML+=`<div class="msg bot-msg">🤖 ${d.answer}</div>`;chatBox.scrollTop=chatBox.scrollHeight;}
function sendQuick(t){document.getElementById('question').value=t;sendMessage();}
document.getElementById('question').addEventListener('keypress',function(e){if(e.key==='Enter')sendMessage();});
</script></body></html>'''

# ===== МАРШРУТЫ =====
@app.route('/')
def home():
    return render_template_string(MAIN_HTML, count=get_count(), posts=get_posts())

@app.route('/portfolio')
def portfolio():
    return render_template_string(PORTFOLIO_HTML)

@app.route('/pricing')
def pricing():
    return render_template_string(PRICING_HTML)

@app.route('/about')
def about():
    return render_template_string(ABOUT_HTML)

@app.route('/blog')
def blog():
    return render_template_string(BLOG_HTML, posts=get_posts())

@app.route('/post/<int:post_id>')
def post(post_id):
    posts = get_posts()
    post = next((p for p in posts if p[0] == post_id), None)
    if post:
        return render_template_string(POST_HTML, post=post)
    return "Пост не найден"

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        message = request.form['message']
        add_message(name, phone, message)
        send_telegram(name, phone, message)
        return render_template_string(SUCCESS_HTML, name=name)
    return render_template_string(CONTACT_HTML)

@app.route('/admin')
@login_required
def admin():
    search = request.args.get('search', '')
    return render_template_string(ADMIN_HTML, messages=get_messages(search), count=get_count(), posts=get_posts(), search=search)

@app.route('/admin/delete/<int:msg_id>')
@login_required
def admin_delete(msg_id):
    delete_message(msg_id)
    return admin()

@app.route('/admin/add_post', methods=['POST'])
@login_required
def add_post_route():
    title = request.form['title']
    content = request.form['content']
    add_post(title, content)
    return admin()

@app.route('/chat')
def chat():
    return render_template_string(CHAT_HTML)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    q = data.get('question', '').lower()
    if 'привет' in q or 'здравствуй' in q:
        answer = random.choice(['Привет! Как дела? 😊', 'Здравствуй! Рад видеть! 👋', 'Хей! Давно не виделись! 🤗'])
    elif 'как дела' in q:
        answer = random.choice(['У меня всё отлично! А у тебя? 😄', 'Супер! Программирую! 🚀', 'Лучше всех! 😎'])
    elif 'имя' in q or 'зовут' in q:
        answer = 'Меня зовут Бот-помощник! 🤖'
    elif 'python' in q or 'питон' in q:
        answer = 'Python — крутой язык программирования! 🐍'
    elif 'бот' in q:
        answer = 'Я умею создавать Telegram-ботов! Хочешь научиться? 🤖'
    elif 'погода' in q:
        answer = 'Погода отличная! 🌤️'
    elif 'спасибо' in q:
        answer = 'Пожалуйста! Рад помочь! 😊'
    elif 'шутка' in q or 'смешное' in q:
        answer = random.choice(['Почему программисты не любят природу? Там много багов! 😂', 'Программист решает проблему, которой у вас не было! 🤓', 'Сколько программистов нужно для замены лампочки? Ни одного — это проблема железа! 💡'])
    elif 'код' in q or 'программирование' in q:
        answer = 'Код — это магия! 💻 Хочешь пример?'
    elif 'сайт' in q or 'flask' in q:
        answer = 'Этот сайт сделан на Flask! 🔥'
    elif 'цена' in q or 'стоит' in q:
        answer = 'Лендинг — 5000₽, Сайт с админкой — 15000₽, Сайт с ботом — 25000₽. Подробнее: /pricing'
    elif 'валют' in q or 'курс' in q:
        try:
            r = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
            d = r.json()
            answer = f'💵 Курсы на сегодня:\n🇺🇸 1 USD = {d["rates"]["RUB"]:.2f} ₽'
        except:
            answer = 'Курс валют временно недоступен 😔'
    elif 'пока' in q or 'до свидания' in q:
        answer = random.choice(['Пока! Возвращайся! 👋', 'До встречи! 😊'])
    else:
        answer = random.choice(['Интересный вопрос! 🤔', 'Ого! Ты меня застал врасплох! 😄', 'Отличный вопрос! Изучу его! 📝', 'Хм, давай подумаем вместе! 🧠'])
    return jsonify({'answer': answer})


# ===== ЛОГИН В АДМИНКУ =====
LOGIN_HTML = '''<!DOCTYPE html>
<html><head><title>Вход в админку</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Arial,sans-serif;background:linear-gradient(135deg,#0b0f1a,#1a1a2e);display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px;color:#fff}
.card{background:rgba(255,255,255,0.05);padding:50px 40px;border-radius:30px;border:1px solid rgba(255,255,255,0.08);max-width:450px;width:100%;text-align:center}
.card i{font-size:70px;color:#6c63ff;margin-bottom:20px}
h1{font-size:28px;margin-bottom:10px}
.sub{color:#888;margin-bottom:25px;font-size:14px}
input{width:100%;padding:15px;margin:10px 0;border-radius:12px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:#fff;font-size:16px}
input:focus{outline:none;border-color:#6c63ff}
button{width:100%;padding:15px;margin-top:15px;border-radius:12px;border:none;background:linear-gradient(135deg,#6c63ff,#ff6b6b);color:#fff;font-size:17px;font-weight:600;cursor:pointer}
button:hover{transform:scale(1.02)}
a{color:#6c63ff;text-decoration:none;display:inline-block;margin-top:15px;font-size:14px}
.error{background:rgba(255,107,107,0.15);color:#ff6b6b;padding:10px;border-radius:10px;margin-bottom:15px;font-size:14px}
</style></head>
<body>
<div class="card">
    <i class="fas fa-lock"></i>
    <h1>Вход в админку</h1>
    <p class="sub">Только для администратора</p>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
        <input type="text" name="username" placeholder="Логин" required autofocus>
        <input type="password" name="password" placeholder="Пароль" required>
        <button type="submit"><i class="fas fa-sign-in-alt"></i> Войти</button>
    </form>
    <a href="/">← На главную</a>
</div>
</body></html>'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['logged_in'] = True
            return redirect('/admin')
        else:
            error = '❌ Неверный логин или пароль'
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

import os

if __name__ == '__main__':
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
