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
<title>Даниил — Премиум веб-разработчик</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
    --bg: #0a0a0a;
    --bg2: #111111;
    --card: #141414;
    --text: #f5f5f5;
    --text2: #a0a0a0;
    --border: rgba(212,175,55,0.2);
    --gold: #d4af37;
    --gold2: #c9a961;
    --gold-light: #e8c968;
}

body {
    font-family: 'Inter', sans-serif;
    background: var(--bg);
    color: var(--text);
    overflow-x: hidden;
    line-height: 1.6;
}

/* ===== ШАПКА ===== */
header {
    background: linear-gradient(180deg, #0a0a0a 0%, #141414 100%);
    padding: 120px 20px 100px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(circle at 50% 50%, rgba(212,175,55,0.15), transparent 60%);
    pointer-events: none;
}
header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 50%;
    transform: translateX(-50%);
    width: 200px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}

.top-label {
    font-size: 12px;
    letter-spacing: 6px;
    color: var(--gold);
    text-transform: uppercase;
    margin-bottom: 25px;
    font-weight: 500;
    animation: fadeIn 1s ease;
}
header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 88px;
    font-weight: 400;
    letter-spacing: -2px;
    margin-bottom: 20px;
    color: var(--text);
    animation: fadeInUp 1s ease;
}
header h1 span {
    color: var(--gold);
    font-style: italic;
}
header p {
    font-size: 18px;
    color: var(--text2);
    font-weight: 300;
    letter-spacing: 1px;
    animation: fadeIn 1.5s ease;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* ===== NAV ===== */
nav {
    background: rgba(10,10,10,0.95);
    backdrop-filter: blur(20px);
    padding: 20px;
    text-align: center;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
    border-bottom: 1px solid rgba(212,175,55,0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}
nav a {
    color: var(--text2);
    text-decoration: none;
    font-weight: 500;
    font-size: 14px;
    letter-spacing: 1px;
    text-transform: uppercase;
    transition: 0.3s;
    padding: 10px 20px;
    position: relative;
}
nav a::after {
    content: '';
    position: absolute;
    bottom: 5px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 1px;
    background: var(--gold);
    transition: 0.3s;
}
nav a:hover { color: var(--gold); }
nav a:hover::after { width: 60%; }

.theme-switcher {
    display: flex;
    gap: 6px;
    margin-left: 20px;
    padding: 4px;
    border: 1px solid rgba(212,175,55,0.2);
    border-radius: 30px;
}
.theme-btn {
    width: 26px; height: 26px;
    border-radius: 50%;
    border: 2px solid transparent;
    cursor: pointer;
    transition: 0.3s;
}
.theme-btn:hover { transform: scale(1.15); }
.theme-btn.active { border-color: var(--gold); }
.theme-btn[data-theme="dark"] { background: linear-gradient(135deg,#0a0a0a,#d4af37); }
.theme-btn[data-theme="light"] { background: linear-gradient(135deg,#fff,#d4af37); }
.theme-btn[data-theme="gold"] { background: linear-gradient(135deg,#0a0a0a,#d4af37); }
.theme-btn[data-theme="ocean"] { background: linear-gradient(135deg,#0a1929,#00d4ff); }

/* ===== CONTAINER ===== */
.container { max-width: 1200px; margin: 0 auto; padding: 0 30px; }

/* ===== HERO SECTION ===== */
.hero {
    padding: 100px 0;
    background: linear-gradient(180deg, #141414 0%, #0a0a0a 100%);
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(212,175,55,0.08), transparent 70%);
    pointer-events: none;
}

.section-label {
    font-size: 11px;
    letter-spacing: 6px;
    color: var(--gold);
    text-transform: uppercase;
    font-weight: 500;
    margin-bottom: 25px;
    display: block;
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 56px;
    font-weight: 400;
    line-height: 1.1;
    margin-bottom: 40px;
    color: var(--text);
}
.section-title span {
    color: var(--gold);
    font-style: italic;
}

/* ===== СТАТИСТИКА ===== */
.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1px;
    background: rgba(212,175,55,0.15);
    border: 1px solid rgba(212,175,55,0.15);
    margin: 60px 0;
}
.stat {
    background: var(--bg);
    padding: 45px 30px;
    text-align: center;
    transition: 0.4s;
}
.stat:hover { background: #141414; }
.stat h2 {
    font-family: 'Playfair Display', serif;
    font-size: 52px;
    font-weight: 400;
    color: var(--gold);
    margin-bottom: 10px;
}
.stat p {
    color: var(--text2);
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ===== УСЛУГИ ===== */
.services {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2px;
    background: rgba(212,175,55,0.15);
    border: 1px solid rgba(212,175,55,0.15);
    margin-top: 50px;
}
.service {
    background: var(--bg);
    padding: 50px 35px;
    transition: 0.5s;
    position: relative;
    overflow: hidden;
}
.service::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(212,175,55,0.05), transparent);
    transition: 0.8s;
}
.service:hover::before { left: 100%; }
.service:hover { background: #141414; transform: translateY(-3px); }
.service i {
    font-size: 36px;
    color: var(--gold);
    margin-bottom: 25px;
    display: block;
}
.service h3 {
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    font-weight: 500;
    margin-bottom: 15px;
    color: var(--text);
}
.service p {
    color: var(--text2);
    font-size: 15px;
    line-height: 1.7;
}

/* ===== ПОРТФОЛИО ===== */
.gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 25px;
    margin-top: 50px;
}
.gallery-item {
    height: 240px;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 30px;
    text-decoration: none;
    color: var(--text);
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(212,175,55,0.2);
    transition: 0.5s;
    font-family: 'Playfair Display', serif;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-size: 16px;
}
.gallery-item::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
    z-index: 0;
    transition: 0.5s;
}
.gallery-item:hover::before {
    background: linear-gradient(135deg, #d4af37, #c9a961);
}
.gallery-item:hover {
    border-color: var(--gold);
    transform: translateY(-8px);
    box-shadow: 0 20px 40px rgba(212,175,55,0.2);
}
.gallery-item span {
    position: relative;
    z-index: 1;
    transition: 0.3s;
}
.gallery-item:hover span { color: #0a0a0a; }
.gallery-item small {
    position: relative;
    z-index: 1;
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    letter-spacing: 3px;
    opacity: 0.7;
    margin-top: 10px;
    color: inherit;
    transition: 0.3s;
}
.gallery-item:hover small { color: #0a0a0a; opacity: 0.9; }

/* ===== ЦЕНЫ ===== */
.pricing {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 25px;
    margin-top: 50px;
}
.price-card {
    background: var(--card);
    padding: 50px 40px;
    border: 1px solid rgba(212,175,55,0.2);
    transition: 0.5s;
    position: relative;
}
.price-card:hover {
    transform: translateY(-10px);
    border-color: var(--gold);
    box-shadow: 0 30px 60px rgba(212,175,55,0.15);
}
.price-card.popular::before {
    content: '★ ПОПУЛЯРНЫЙ';
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--gold);
    color: #0a0a0a;
    padding: 5px 20px;
    font-size: 10px;
    letter-spacing: 3px;
    font-weight: 700;
}
.price-card h3 {
    font-family: 'Playfair Display', serif;
    font-size: 26px;
    font-weight: 500;
    margin-bottom: 20px;
    color: var(--text);
}
.price-card .price {
    font-family: 'Playfair Display', serif;
    font-size: 52px;
    color: var(--gold);
    font-weight: 400;
    margin: 25px 0;
}
.price-card ul {
    list-style: none;
    margin: 30px 0;
}
.price-card li {
    padding: 12px 0;
    color: var(--text2);
    border-bottom: 1px solid rgba(212,175,55,0.1);
    font-size: 15px;
}
.price-card li:last-child { border-bottom: none; }
.price-card li i {
    color: var(--gold);
    margin-right: 12px;
    font-size: 12px;
}

/* ===== ОТЗЫВЫ ===== */
.reviews {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 25px;
    margin-top: 50px;
}
.review {
    background: var(--card);
    padding: 40px;
    border: 1px solid rgba(212,175,55,0.15);
    position: relative;
    transition: 0.4s;
}
.review::before {
    content: '"';
    position: absolute;
    top: 15px; left: 25px;
    font-family: 'Playfair Display', serif;
    font-size: 80px;
    color: var(--gold);
    opacity: 0.3;
    line-height: 1;
}
.review:hover {
    border-color: var(--gold);
    transform: translateY(-5px);
}
.review p {
    color: var(--text2);
    font-style: italic;
    line-height: 1.8;
    margin-bottom: 20px;
    position: relative;
    z-index: 1;
    font-size: 15px;
}
.review .author {
    color: var(--gold);
    font-weight: 500;
    letter-spacing: 1px;
    font-size: 14px;
}
.review .stars {
    color: var(--gold);
    margin-bottom: 15px;
    font-size: 14px;
    letter-spacing: 3px;
}

/* ===== FAQ ===== */
.faq {
    margin-top: 50px;
}
.faq-item {
    background: var(--card);
    border: 1px solid rgba(212,175,55,0.15);
    margin-bottom: 15px;
    transition: 0.3s;
    cursor: pointer;
}
.faq-item:hover { border-color: var(--gold); }
.faq-question {
    padding: 25px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: var(--text);
    font-family: 'Playfair Display', serif;
    font-size: 18px;
    font-weight: 500;
}
.faq-question i {
    color: var(--gold);
    transition: 0.3s;
    font-size: 14px;
}
.faq-item.active .faq-question i { transform: rotate(45deg); }
.faq-answer {
    max-height: 0;
    overflow: hidden;
    transition: 0.4s;
    padding: 0 30px;
    color: var(--text2);
    line-height: 1.8;
    font-size: 15px;
}
.faq-item.active .faq-answer {
    max-height: 300px;
    padding: 0 30px 25px;
}

/* ===== КНОПКА ===== */
.btn {
    display: inline-block;
    background: transparent;
    color: var(--gold);
    padding: 18px 45px;
    border: 1px solid var(--gold);
    text-decoration: none;
    font-weight: 500;
    font-size: 13px;
    letter-spacing: 4px;
    text-transform: uppercase;
    transition: 0.4s;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.btn::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: var(--gold);
    transition: 0.5s;
    z-index: 0;
}
.btn:hover::before { left: 0; }
.btn:hover { color: #0a0a0a; }
.btn span { position: relative; z-index: 1; }

/* ===== FOOTER ===== */
footer {
    background: #000;
    padding: 60px 0 30px;
    text-align: center;
    border-top: 1px solid rgba(212,175,55,0.1);
    margin-top: 80px;
}
footer p {
    color: var(--text2);
    font-size: 13px;
    letter-spacing: 2px;
    margin-bottom: 20px;
}
.footer-links a {
    color: var(--gold);
    margin: 0 15px;
    text-decoration: none;
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
    transition: 0.3s;
}
.footer-links a:hover { color: var(--gold-light); }

/* ===== КОНТАКТЫ ===== */
.contact-section {
    background: linear-gradient(135deg, #0a0a0a, #141414);
    padding: 80px 0;
    text-align: center;
    border-top: 1px solid rgba(212,175,55,0.1);
    border-bottom: 1px solid rgba(212,175,55,0.1);
    position: relative;
}
.contact-section h2 {
    font-family: 'Playfair Display', serif;
    font-size: 48px;
    font-weight: 400;
    margin-bottom: 20px;
}
.contact-section h2 span { color: var(--gold); font-style: italic; }
.contact-section p {
    color: var(--text2);
    margin-bottom: 40px;
    font-size: 16px;
}
.contact-buttons {
    display: flex;
    justify-content: center;
    gap: 15px;
    flex-wrap: wrap;
}
.contact-btn {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 18px 35px;
    border: 1px solid var(--gold);
    color: var(--gold);
    text-decoration: none;
    font-size: 13px;
    letter-spacing: 3px;
    text-transform: uppercase;
    transition: 0.4s;
}
.contact-btn:hover {
    background: var(--gold);
    color: #0a0a0a;
}
.contact-btn i { font-size: 16px; }

/* ===== SECTION SPACING ===== */
.section {
    padding: 100px 0;
}

/* ===== АДАПТИВ ===== */
@media (max-width: 768px) {
    header h1 { font-size: 48px; }
    .section-title { font-size: 36px; }
    .section { padding: 60px 0; }
    nav a { font-size: 12px; padding: 8px 12px; }
    .theme-switcher { margin-left: 0; margin-top: 10px; }
    .contact-section h2 { font-size: 32px; }
}
</style>
</head>
<body>

<header>
    <div class="top-label">Даниил · Веб-разработчик</div>
    <h1>Премиум-сайты<br>для вашего <span>бизнеса</span></h1>
    <p>Создаю сайты, которые работают и продают</p>
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

<!-- HERO SECTION -->
<section class="hero">
    <div class="container">
        <div class="stats">
            <div class="stat"><h2 data-count="4">0</h2><p>Проектов</p></div>
            <div class="stat"><h2 data-count="{{ count }}">{{ count }}</h2><p>Заявок</p></div>
            <div class="stat"><h2>100%</h2><p>На Python</p></div>
            <div class="stat"><h2>24/7</h2><p>На связи</p></div>
        </div>
    </div>
</section>

<!-- УСЛУГИ -->
<section class="section">
    <div class="container">
        <span class="section-label">Услуги</span>
        <h2 class="section-title">Что я <span>делаю</span></h2>
        <div class="services">
            <div class="service">
                <i class="fas fa-code"></i>
                <h3>Сайты на Python</h3>
                <p>Премиум-сайты с админкой, базой данных и современным дизайном</p>
            </div>
            <div class="service">
                <i class="fas fa-robot"></i>
                <h3>Telegram-боты</h3>
                <p>Автоматизация бизнеса через Telegram. Приём заявок, уведомления</p>
            </div>
            <div class="service">
                <i class="fas fa-gem"></i>
                <h3>Премиум-дизайн</h3>
                <p>Элегантные решения с анимациями и вниманием к деталям</p>
            </div>
            <div class="service">
                <i class="fas fa-database"></i>
                <h3>Веб-приложения</h3>
                <p>CRM-системы, личные кабинеты, дашборды с аналитикой</p>
            </div>
        </div>
    </div>
</section>

<!-- ПОРТФОЛИО -->
<section class="section">
    <div class="container">
        <span class="section-label">Портфолио</span>
        <h2 class="section-title">Мои <span>работы</span></h2>
        <div class="gallery">
            <a href="https://p6874435-svg.github.io/spa-demo/" target="_blank" class="gallery-item">
                <span>Студия Евгении</span>
                <small>SPA · МАССАЖ</small>
            </a>
            <a href="https://p6874435-svg.github.io/manifik-minimal/manifikminimal.html" target="_blank" class="gallery-item">
                <span>Dr. Manifik</span>
                <small>КОСМЕТОЛОГИЯ · MINIMAL</small>
            </a>
            <a href="https://p6874435-svg.github.io/manifik-minimal/manifikpremium.html" target="_blank" class="gallery-item">
                <span>Dr. Manifik Premium</span>
                <small>КОСМЕТОЛОГИЯ · PREMIUM</small>
            </a>
            <a href="https://p6874435-svg.github.io/manifik-minimal/irina_kosmetolog_demo.html" target="_blank" class="gallery-item">
                <span>Ирина</span>
                <small>КОСМЕТОЛОГ · ЯЛТА</small>
            </a>
        </div>
    </div>
</section>

<!-- ЦЕНЫ -->
<section class="section">
    <div class="container">
        <span class="section-label">Стоимость</span>
        <h2 class="section-title">Мои <span>цены</span></h2>
        <div class="pricing">
            <div class="price-card">
                <h3>Лендинг</h3>
                <div class="price">5 000 ₽</div>
                <ul>
                    <li><i class="fas fa-check"></i>Одностраничный сайт</li>
                    <li><i class="fas fa-check"></i>Адаптивный дизайн</li>
                    <li><i class="fas fa-check"></i>Форма заявки</li>
                    <li><i class="fas fa-check"></i>Срок: 2-3 дня</li>
                </ul>
                <a href="/contact" class="btn"><span>Заказать</span></a>
            </div>
            <div class="price-card popular">
                <h3>Сайт + Админка</h3>
                <div class="price">15 000 ₽</div>
                <ul>
                    <li><i class="fas fa-check"></i>Многостраничный сайт</li>
                    <li><i class="fas fa-check"></i>Админ-панель</li>
                    <li><i class="fas fa-check"></i>База данных</li>
                    <li><i class="fas fa-check"></i>Срок: 5-7 дней</li>
                </ul>
                <a href="/contact" class="btn"><span>Заказать</span></a>
            </div>
            <div class="price-card">
                <h3>Сайт + Бот</h3>
                <div class="price">25 000 ₽</div>
                <ul>
                    <li><i class="fas fa-check"></i>Всё из «+ Админка»</li>
                    <li><i class="fas fa-check"></i>Telegram-бот</li>
                    <li><i class="fas fa-check"></i>Уведомления в TG</li>
                    <li><i class="fas fa-check"></i>Срок: 7-10 дней</li>
                </ul>
                <a href="/contact" class="btn"><span>Заказать</span></a>
            </div>
        </div>
    </div>
</section>

<!-- ОТЗЫВЫ -->
<section class="section">
    <div class="container">
        <span class="section-label">Отзывы</span>
        <h2 class="section-title">Что говорят <span>клиенты</span></h2>
        <div class="reviews">
            <div class="review">
                <div class="stars">★★★★★</div>
                <p>Даниил сделал сайт для моей студии за 3 дня. Работает быстро, красиво и удобно. Клиенты довольны!</p>
                <div class="author">Евгения И. · Студия SPA</div>
            </div>
            <div class="review">
                <div class="stars">★★★★★</div>
                <p>Отличный сайт для косметологии. Всё сделано профессионально, с вниманием к деталям. Рекомендую!</p>
                <div class="author">Ирина К. · Косметолог</div>
            </div>
            <div class="review">
                <div class="stars">★★★★★</div>
                <p>Заказывал сайт для клиники. Результат превзошёл ожидания! Сайт загружается быстро, выглядит премиально.</p>
                <div class="author">Дмитрий М. · Клиника</div>
            </div>
        </div>
    </div>
</section>

<!-- FAQ -->
<section class="section">
    <div class="container">
        <span class="section-label">FAQ</span>
        <h2 class="section-title">Частые <span>вопросы</span></h2>
        <div class="faq">
            <div class="faq-item" onclick="toggleFaq(this)">
                <div class="faq-question">Сколько стоит сайт? <i class="fas fa-plus"></i></div>
                <div class="faq-answer">Цены начинаются от 5 000 ₽ за лендинг. Полный сайт с админкой — от 15 000 ₽. Сайт с Telegram-ботом — от 25 000 ₽.</div>
            </div>
            <div class="faq-item" onclick="toggleFaq(this)">
                <div class="faq-question">Сколько времени делается сайт? <i class="fas fa-plus"></i></div>
                <div class="faq-answer">Лендинг — 2-3 дня. Сайт с админкой — 5-7 дней. Сайт с ботом — 7-10 дней. Точные сроки обсудим после уточнения задачи.</div>
            </div>
            <div class="faq-item" onclick="toggleFaq(this)">
                <div class="faq-question">Что входит в стоимость? <i class="fas fa-plus"></i></div>
                <div class="faq-answer">Дизайн, разработка, адаптив под телефоны, запуск на хостинге, обучение по использованию админки. Домен и хостинг оплачиваются отдельно (~500 ₽/год).</div>
            </div>
            <div class="faq-item" onclick="toggleFaq(this)">
                <div class="faq-question">Можно потом доработать сайт? <i class="fas fa-plus"></i></div>
                <div class="faq-answer">Да, конечно! Я всегда на связи. Мелкие доработки — бесплатно в течение месяца после сдачи. Крупные изменения — по договорённости.</div>
            </div>
            <div class="faq-item" onclick="toggleFaq(this)">
                <div class="faq-question">Как происходит оплата? <i class="fas fa-plus"></i></div>
                <div class="faq-answer">50% предоплата, 50% после сдачи работы. Работаю по договору или самозанятости. Все чеки и документы предоставляю.</div>
            </div>
            <div class="faq-item" onclick="toggleFaq(this)">
                <div class="faq-question">Есть ли гарантия? <i class="fas fa-plus"></i></div>
                <div class="faq-answer">Да, месяц гарантии на все работы. Если что-то сломается — исправлю бесплатно. Также помогаю с настройкой после сдачи.</div>
            </div>
        </div>
    </div>
</section>

<!-- КОНТАКТЫ -->
<section class="contact-section">
    <div class="container">
        <h2>Готовы обсудить <span>проект?</span></h2>
        <p>Напишите мне — обсудим задачу, сроки и стоимость</p>
        <div class="contact-buttons">
            <a href="https://t.me/ponomera2" target="_blank" class="contact-btn">
                <i class="fab fa-telegram"></i> Telegram
            </a>
            <a href="mailto:ponomarenkodana410@gmail.com" class="contact-btn">
                <i class="fas fa-envelope"></i> Email
            </a>
            <a href="/contact" class="contact-btn">
                <i class="fas fa-paper-plane"></i> Оставить заявку
            </a>
        </div>
    </div>
</section>

<footer>
    <p>© 2026 ДАНИИЛ · ВЕБ-РАЗРАБОТЧИК</p>
    <div class="footer-links">
        <a href="/">Главная</a>
        <a href="/portfolio">Портфолио</a>
        <a href="/pricing">Цены</a>
        <a href="/blog">Блог</a>
        <a href="/contact">Контакты</a>
        <a href="/admin">Админ</a>
    </div>
</footer>

<script>
// Переключение темы
function setTheme(theme) {
    document.body.className = 'theme-' + theme;
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === theme);
    });
    localStorage.setItem('site-theme', theme);
}
const savedTheme = localStorage.getItem('site-theme') || 'dark';
setTheme(savedTheme);

// FAQ
function toggleFaq(el) {
    el.classList.toggle('active');
}

// Счётчик
const counters = document.querySelectorAll('[data-count]');
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.dataset.done) {
            entry.target.dataset.done = true;
            const target = +entry.target.dataset.count;
            let current = 0;
            const step = Math.max(1, Math.floor(target / 40));
            const timer = setInterval(() => {
                current += step;
                if (current >= target) { current = target; clearInterval(timer); }
                entry.target.textContent = current;
            }, 30);
        }
    });
}, { threshold: 0.5 });
counters.forEach(c => observer.observe(c));
</script>

</body>
</html>
'''

ABOUT_HTML = '''<!DOCTYPE html><html><head><title>О нас</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Segoe UI,Arial,sans-serif;background:#0b0f1a;color:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px}.card{background:rgba(255,255,255,0.05);border-radius:30px;border:1px solid rgba(255,255,255,0.08);max-width:700px;width:100%;padding:50px;text-align:center}.avatar i{font-size:100px;color:#6c63ff;background:rgba(108,99,255,0.15);padding:30px;border-radius:50%}h1{font-size:36px;margin:20px 0 10px}.subtitle{color:#6c63ff;font-size:18px}.bio{color:#aaa;line-height:1.8;margin:20px 0}.btn{display:inline-block;background:#6c63ff;color:#fff;padding:12px 30px;border-radius:50px;text-decoration:none;font-weight:600;margin-top:20px}</style></head><body><div class="card"><div class="avatar"><i class="fas fa-user-astronaut"></i></div><h1>👋 Привет, я Даниил!</h1><p class="subtitle">Веб-разработчик на Python</p><div class="bio">Создаю сайты, Telegram-ботов и веб-приложения. Люблю учиться новому и решать сложные задачи.</div><a href="/" class="btn">На главную</a></div></body></html>'''

PORTFOLIO_HTML = '''<!DOCTYPE html><html><head><title>Портфолио</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0f1a;color:#fff;font-family:Segoe UI,Arial,sans-serif;padding:40px 20px}.container{max-width:1100px;margin:0 auto}.card{background:rgba(255,255,255,0.05);padding:40px;border-radius:25px;border:1px solid rgba(255,255,255,0.08)}h1{text-align:center;font-size:42px;margin-bottom:15px}.sub{text-align:center;color:#aaa;margin-bottom:40px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:25px}.item{display:block;background:rgba(255,255,255,0.05);border-radius:20px;overflow:hidden;transition:0.3s;border:1px solid rgba(255,255,255,0.05);text-decoration:none;color:inherit}.item:hover{transform:translateY(-10px);border-color:#6c63ff}.preview{height:200px;display:flex;align-items:center;justify-content:center;font:600 22px Georgia;color:#fff;letter-spacing:3px}.item:nth-child(1) .preview{background:linear-gradient(135deg,#d8c0ad,#9d765e)}.item:nth-child(2) .preview{background:linear-gradient(135deg,#eaded4,#c3a28c)}.item:nth-child(3) .preview{background:linear-gradient(135deg,#cfc2b4,#8f8173)}.item:nth-child(4) .preview{background:linear-gradient(135deg,#e8ddd5,#bda18e)}.info{padding:25px}.info h3{font-size:20px;margin-bottom:10px}.info p{color:#aaa;font-size:14px;margin-bottom:15px}.tags span{display:inline-block;background:rgba(108,99,255,0.15);color:#9d94ff;padding:5px 12px;border-radius:20px;font-size:12px;font-weight:600;margin-right:5px}.back{color:#6c63ff;text-decoration:none;display:block;margin-top:20px;text-align:center}</style></head><body><div class="container"><div class="card"><h1>💼 Мои работы</h1><p class="sub">Демо-сайты, которые я сделал</p><div class="grid"><a href="https://p6874435-svg.github.io/spa-demo/" target="_blank" class="item"><div class="preview">SPA STUDIO</div><div class="info"><h3>Студия Евгении</h3><p>Сайт студии SPA-массажа</p><div class="tags"><span>Сайт</span><span>SPA</span></div></div></a><a href="https://p6874435-svg.github.io/manifik-minimal/manifikminimal.html" target="_blank" class="item"><div class="preview">MANIFIK</div><div class="info"><h3>Dr. Manifik — Minimal</h3><p>Клиника косметологии</p><div class="tags"><span>Сайт</span><span>Медицина</span></div></div></a><a href="https://p6874435-svg.github.io/manifik-minimal/manifikpremium.html" target="_blank" class="item"><div class="preview">PREMIUM</div><div class="info"><h3>Dr. Manifik — Premium</h3><p>Премиум-версия сайта</p><div class="tags"><span>Сайт</span><span>Премиум</span></div></div></a><a href="https://p6874435-svg.github.io/manifik-minimal/irina_kosmetolog_demo.html" target="_blank" class="item"><div class="preview">IRINA</div><div class="info"><h3>Ирина — косметолог</h3><p>Сайт косметолога из Ялты</p><div class="tags"><span>Сайт</span><span>Косметология</span></div></div></a></div><a href="/" class="back">← На главную</a></div></div></body></html>'''

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
