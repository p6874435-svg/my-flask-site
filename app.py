from flask import Flask, request, render_template_string, jsonify, session, redirect, url_for, make_response
from functools import wraps
import sqlite3
from datetime import datetime
import random
import requests
import csv
import io

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
USER_ID = "7443989455"

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
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Даниил — Премиум веб-разработчик | Сайты, боты, веб-приложения</title>
<meta name="description" content="Создаю премиум-сайты на Python, Telegram-ботов и веб-приложения. От 5000 руб. Срок от 2 дней.">
<meta name="author" content="Даниил Пономаренко">
<meta name="robots" content="index, follow">
<link rel="icon" href="https://cdn-icons-png.flaticon.com/512/616/616494.png">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
    --bg: #faf8f5;
    --bg2: #f5f1eb;
    --card: #ffffff;
    --text: #2a2a2a;
    --text2: #6b6b6b;
    --border: rgba(184,134,11,0.15);
    --gold: #b8860b;
    --gold2: #9a7009;
    --gold-light: #d4a017;
    --dark: #1a1a1a;
}
body.theme-dark { --bg: #0a0a0a; --bg2: #141414; --card: #1a1a1a; --text: #f5f5f5; --text2: #a0a0a0; --border: rgba(184,134,11,0.2); --dark: #000; }
body.theme-dark header, body.theme-dark .page-header { background: linear-gradient(180deg, #141414 0%, #0a0a0a 100%); }
body.theme-dark nav { background: rgba(10,10,10,0.95); }
body.theme-gold { --bg: #0a0a0a; --bg2: #141208; --card: #1a1810; --text: #f5f5f5; --text2: #c9a961; --border: rgba(212,175,55,0.3); --gold: #d4af37; --gold2: #b8941f; --gold-light: #e8c968; --dark: #000; }
body.theme-gold header, body.theme-gold .page-header { background: linear-gradient(180deg, #141208 0%, #0a0a0a 100%); }
body.theme-gold nav { background: rgba(10,10,10,0.95); }
body.theme-ocean { --bg: #0a1929; --bg2: #0f2438; --card: #142a40; --text: #e3f2fd; --text2: #64b5f6; --border: rgba(0,212,255,0.2); --gold: #00d4ff; --gold2: #0095d4; --gold-light: #4de3ff; --dark: #04121f; }
body.theme-ocean header, body.theme-ocean .page-header { background: linear-gradient(180deg, #0f2438 0%, #0a1929 100%); }
body.theme-ocean nav { background: rgba(10,25,41,0.95); }

body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); overflow-x: hidden; line-height: 1.6; transition: 0.3s; }

/* Анимации при скролле */
.reveal {
    opacity: 0;
    transform: translateY(40px);
    transition: opacity 0.8s ease, transform 0.8s ease;
}
.reveal.active {
    opacity: 1;
    transform: translateY(0);
}
.reveal-delay-1 { transition-delay: 0.1s; }
.reveal-delay-2 { transition-delay: 0.2s; }
.reveal-delay-3 { transition-delay: 0.3s; }
.reveal-delay-4 { transition-delay: 0.4s; }

header { background: linear-gradient(180deg, #ffffff 0%, #faf8f5 100%); padding: 120px 20px 100px; text-align: center; position: relative; overflow: hidden; border-bottom: 1px solid var(--border); }
header::before { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(circle at 50% 50%, rgba(184,134,11,0.08), transparent 60%); pointer-events: none; }
header::after { content: ''; position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 200px; height: 1px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }
.top-label { font-size: 12px; letter-spacing: 6px; color: var(--gold); text-transform: uppercase; margin-bottom: 25px; font-weight: 600; }
header h1 { font-family: 'Playfair Display', serif; font-size: 88px; font-weight: 400; letter-spacing: -2px; margin-bottom: 20px; color: var(--text); }
header h1 span { color: var(--gold); font-style: italic; }
header p { font-size: 18px; color: var(--text2); font-weight: 300; letter-spacing: 1px; }

nav { background: rgba(255,255,255,0.95); backdrop-filter: blur(20px); padding: 20px; text-align: center; display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 8px; border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; }
.nav-links { display: flex; justify-content: center; flex-wrap: wrap; gap: 8px; align-items: center; }
nav a { color: var(--text2); text-decoration: none; font-weight: 500; font-size: 14px; letter-spacing: 1px; text-transform: uppercase; transition: 0.3s; padding: 10px 20px; position: relative; }
nav a::after { content: ''; position: absolute; bottom: 5px; left: 50%; transform: translateX(-50%); width: 0; height: 1px; background: var(--gold); transition: 0.3s; }
nav a:hover { color: var(--gold); }
nav a:hover::after { width: 60%; }

.burger { display: none; background: none; border: none; cursor: pointer; padding: 10px; flex-direction: column; gap: 5px; position: absolute; right: 20px; top: 50%; transform: translateY(-50%); }
.burger span { display: block; width: 25px; height: 2px; background: var(--gold); transition: 0.3s; }
.burger.active span:nth-child(1) { transform: rotate(45deg) translate(5px, 5px); }
.burger.active span:nth-child(2) { opacity: 0; }
.burger.active span:nth-child(3) { transform: rotate(-45deg) translate(5px, -5px); }

.theme-switcher { display: flex; gap: 6px; margin-left: 20px; padding: 4px; border: 1px solid var(--border); border-radius: 30px; background: white; }
.theme-btn { width: 26px; height: 26px; border-radius: 50%; border: 2px solid transparent; cursor: pointer; transition: 0.3s; }
.theme-btn:hover { transform: scale(1.15); }
.theme-btn.active { border-color: var(--gold); }
.theme-btn[data-theme="dark"] { background: linear-gradient(135deg,#1a1a1a,#b8860b); }
.theme-btn[data-theme="light"] { background: linear-gradient(135deg,#fff,#b8860b); }
.theme-btn[data-theme="gold"] { background: linear-gradient(135deg,#1a1a1a,#d4af37); }
.theme-btn[data-theme="ocean"] { background: linear-gradient(135deg,#0a1929,#00d4ff); }

.container { max-width: 1200px; margin: 0 auto; padding: 0 30px; }
.section { padding: 100px 0; }

.section-label { font-size: 11px; letter-spacing: 6px; color: var(--gold); text-transform: uppercase; font-weight: 600; margin-bottom: 25px; display: block; }
.section-title { font-family: 'Playfair Display', serif; font-size: 56px; font-weight: 400; line-height: 1.1; margin-bottom: 40px; color: var(--text); }
.section-title span { color: var(--gold); font-style: italic; }

.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1px; background: var(--border); border: 1px solid var(--border); margin: 60px 0; border-radius: 8px; overflow: hidden; }
.stat { background: white; padding: 45px 30px; text-align: center; }
.stat h2 { font-family: 'Playfair Display', serif; font-size: 52px; color: var(--gold); margin-bottom: 10px; }
.stat p { color: var(--text2); font-size: 13px; letter-spacing: 2px; text-transform: uppercase; }

.services { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2px; background: var(--border); border: 1px solid var(--border); margin-top: 50px; border-radius: 8px; overflow: hidden; }
.service { background: white; padding: 50px 35px; transition: 0.5s; position: relative; overflow: hidden; }
.service:hover { background: #fdfbf7; }
.service i { font-size: 36px; color: var(--gold); margin-bottom: 25px; display: block; }
.service h3 { font-family: 'Playfair Display', serif; font-size: 24px; margin-bottom: 15px; color: var(--text); }
.service p { color: var(--text2); font-size: 15px; }

.gallery { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin-top: 50px; }
.gallery-item { height: 240px; border-radius: 4px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 30px; text-decoration: none; color: white; position: relative; overflow: hidden; border: 1px solid var(--border); transition: 0.5s; font-family: 'Playfair Display', serif; letter-spacing: 3px; text-transform: uppercase; font-size: 16px; }
.gallery-item::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, #2a2a2a, #4a4a4a); z-index: 0; transition: 0.5s; }
.gallery-item:hover::before { background: linear-gradient(135deg, #b8860b, #d4a017); }
.gallery-item:hover { border-color: var(--gold); transform: translateY(-8px); box-shadow: 0 20px 40px rgba(184,134,11,0.3); }
.gallery-item span { position: relative; z-index: 1; }
.gallery-item small { position: relative; z-index: 1; font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 3px; opacity: 0.7; margin-top: 10px; }

.pricing { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin-top: 50px; }
.price-card { background: white; padding: 50px 40px; border: 1px solid var(--border); transition: 0.5s; position: relative; border-radius: 8px; }
.price-card:hover { transform: translateY(-10px); border-color: var(--gold); box-shadow: 0 30px 60px rgba(184,134,11,0.15); }
.price-card.popular::before { content: '★ ПОПУЛЯРНЫЙ'; position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: var(--gold); color: white; padding: 5px 20px; font-size: 10px; letter-spacing: 3px; font-weight: 700; border-radius: 20px; }
.price-card h3 { font-family: 'Playfair Display', serif; font-size: 26px; margin-bottom: 20px; color: var(--text); }
.price-card .price { font-family: 'Playfair Display', serif; font-size: 52px; color: var(--gold); margin: 25px 0; }
.price-card ul { list-style: none; margin: 30px 0; }
.price-card li { padding: 12px 0; color: var(--text2); border-bottom: 1px solid var(--border); font-size: 15px; }
.price-card li:last-child { border-bottom: none; }
.price-card li i { color: var(--gold); margin-right: 12px; font-size: 12px; }

.reviews { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin-top: 50px; }
.review { background: white; padding: 40px; border: 1px solid var(--border); position: relative; border-radius: 8px; }
.review::before { content: '"'; position: absolute; top: 15px; left: 25px; font-family: 'Playfair Display', serif; font-size: 80px; color: var(--gold); opacity: 0.25; line-height: 1; }
.review:hover { border-color: var(--gold); transform: translateY(-5px); box-shadow: 0 20px 40px rgba(184,134,11,0.1); }
.review p { color: var(--text2); font-style: italic; line-height: 1.8; margin-bottom: 20px; position: relative; z-index: 1; font-size: 15px; }
.review .author { color: var(--gold); font-weight: 600; letter-spacing: 1px; font-size: 14px; }
.review .stars { color: var(--gold); margin-bottom: 15px; font-size: 14px; letter-spacing: 3px; }

.faq { margin-top: 50px; }
.faq-item { background: white; border: 1px solid var(--border); margin-bottom: 15px; cursor: pointer; border-radius: 8px; }
.faq-item:hover { border-color: var(--gold); }
.faq-question { padding: 25px 30px; display: flex; justify-content: space-between; align-items: center; color: var(--text); font-family: 'Playfair Display', serif; font-size: 18px; }
.faq-question i { color: var(--gold); transition: 0.3s; font-size: 14px; }
.faq-item.active .faq-question i { transform: rotate(45deg); }
.faq-answer { max-height: 0; overflow: hidden; transition: 0.4s; padding: 0 30px; color: var(--text2); line-height: 1.8; font-size: 15px; }
.faq-item.active .faq-answer { max-height: 300px; padding: 0 30px 25px; }

.btn { display: inline-block; background: transparent; color: var(--gold); padding: 18px 45px; border: 1px solid var(--gold); text-decoration: none; font-weight: 500; font-size: 13px; letter-spacing: 4px; text-transform: uppercase; transition: 0.4s; cursor: pointer; position: relative; overflow: hidden; border-radius: 4px; }
.btn::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: var(--gold); transition: 0.5s; z-index: 0; }
.btn:hover::before { left: 0; }
.btn:hover { color: white; }
.btn span { position: relative; z-index: 1; }

.contact-section { background: linear-gradient(135deg, #1a1a1a, #2a2a2a); padding: 80px 0; text-align: center; color: white; }
.contact-section h2 { font-family: 'Playfair Display', serif; font-size: 48px; margin-bottom: 20px; color: white; }
.contact-section h2 span { color: var(--gold-light); font-style: italic; }
.contact-section p { color: #b0b0b0; margin-bottom: 40px; font-size: 16px; }
.contact-buttons { display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; }
.contact-btn { display: inline-flex; align-items: center; gap: 12px; padding: 18px 35px; border: 1px solid var(--gold); color: var(--gold-light); text-decoration: none; font-size: 13px; letter-spacing: 3px; text-transform: uppercase; transition: 0.4s; border-radius: 4px; }
.contact-btn:hover { background: var(--gold); color: white; }

footer { background: var(--dark); padding: 60px 0 30px; text-align: center; margin-top: 80px; }
footer p { color: #999; font-size: 13px; letter-spacing: 2px; margin-bottom: 20px; }
.footer-links a { color: var(--gold); margin: 0 15px; text-decoration: none; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; transition: 0.3s; }

@media (max-width: 768px) {
    header h1 { font-size: 48px; }
    .section-title { font-size: 36px; }
    .section { padding: 60px 0; }
    .burger { display: flex; }
    .nav-links { display: none; flex-direction: column; width: 100%; padding-top: 15px; }
    .nav-links.active { display: flex; }
    .nav-links a { width: 100%; text-align: center; padding: 12px; }
    .theme-switcher { margin: 10px auto 0; }
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
    <button class="burger" onclick="toggleMenu()">
        <span></span>
        <span></span>
        <span></span>
    </button>
    <div class="nav-links" id="navLinks">
        <a href="/">Главная</a>
        <a href="/services">Услуги</a>
        <a href="/calculator">Калькулятор</a>
        <a href="/portfolio">Портфолио</a>
        <a href="/pricing">Цены</a>
        <a href="/blog">Блог</a>
        <a href="/contact">Контакты</a>
        <a href="/admin">Админ</a>
        <a href="/chat">Чат-бот</a>
        <div class="theme-switcher">
            <button class="theme-btn active" data-theme="light" onclick="setTheme('light')" title="Светлая">☀️</button>
            <button class="theme-btn" data-theme="dark" onclick="setTheme('dark')" title="Тёмная">🌙</button>
            <button class="theme-btn" data-theme="gold" onclick="setTheme('gold')" title="Золотая">👑</button>
            <button class="theme-btn" data-theme="ocean" onclick="setTheme('ocean')" title="Океан">🌊</button>
        </div>
    </div>
</nav>

<section class="section" style="background: var(--bg2); border-bottom: 1px solid var(--border);">
    <div class="container">
        <div class="stats">
            <div class="stat"><h2 data-count="4">0</h2><p>Проектов</p></div>
            <div class="stat"><h2 data-count="{{ count }}">{{ count }}</h2><p>Заявок</p></div>
            <div class="stat"><h2>100%</h2><p>На Python</p></div>
            <div class="stat"><h2>24/7</h2><p>На связи</p></div>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <span class="section-label reveal">Стоимость</span>
        <h2 class="section-title reveal">Мои <span>цены</span></h2>
        <div class="pricing">
            <div class="price-card reveal reveal-delay-1">
                <h3>Лендинг</h3>
                <div class="price">5 000 ₽</div>
                <ul><li><i class="fas fa-check"></i>Одностраничный сайт</li><li><i class="fas fa-check"></i>Адаптивный дизайн</li><li><i class="fas fa-check"></i>Форма заявки</li><li><i class="fas fa-check"></i>Срок: 2-3 дня</li></ul>
                <a href="/contact" class="btn"><span>Заказать</span></a>
            </div>
            <div class="price-card popular reveal reveal-delay-2">
                <h3>Сайт + Админка</h3>
                <div class="price">15 000 ₽</div>
                <ul><li><i class="fas fa-check"></i>Многостраничный сайт</li><li><i class="fas fa-check"></i>Админ-панель</li><li><i class="fas fa-check"></i>База данных</li><li><i class="fas fa-check"></i>Срок: 5-7 дней</li></ul>
                <a href="/contact" class="btn"><span>Заказать</span></a>
            </div>
            <div class="price-card reveal reveal-delay-3">
                <h3>Сайт + Бот</h3>
                <div class="price">25 000 ₽</div>
                <ul><li><i class="fas fa-check"></i>Всё из «+ Админка»</li><li><i class="fas fa-check"></i>Telegram-бот</li><li><i class="fas fa-check"></i>Уведомления в TG</li><li><i class="fas fa-check"></i>Срок: 7-10 дней</li></ul>
                <a href="/contact" class="btn"><span>Заказать</span></a>
            </div>
        </div>
    </div>
</section>

<section class="section">
       <div class="container">
        <span class="section-label reveal">Портфолио</span>
        <h2 class="section-title reveal">Мои <span>работы</span></h2>
        <div class="gallery">
            <a href="https://p6874435-svg.github.io/spa-demo/" target="_blank" class="gallery-item reveal reveal-delay-1"><span>Студия Евгении</span><small>SPA · МАССАЖ</small></a>
            <a href="https://p6874435-svg.github.io/manifik-minimal/manifikminimal.html" target="_blank" class="gallery-item reveal reveal-delay-2"><span>Dr. Manifik</span><small>КОСМЕТОЛОГИЯ · MINIMAL</small></a>
            <a href="https://p6874435-svg.github.io/manifik-minimal/manifikpremium.html" target="_blank" class="gallery-item reveal reveal-delay-3"><span>Dr. Manifik Premium</span><small>КОСМЕТОЛОГИЯ · PREMIUM</small></a>
            <a href="https://p6874435-svg.github.io/manifik-minimal/irina_kosmetolog_demo.html" target="_blank" class="gallery-item reveal reveal-delay-4"><span>Ирина</span><small>КОСМЕТОЛОГ · ЯЛТА</small></a>
        </div>
        <div style="text-align:center; margin-top:60px" class="reveal">
            <a href="/calculator" class="btn"><span>Рассчитать стоимость →</span></a>
        </div>
    </div>
</section>

<section class="contact-section">
    <div class="container">
        <h2 class="reveal">Готовы обсудить <span>проект?</span></h2>
        <p class="reveal">Напишите мне — обсудим задачу, сроки и стоимость</p>
        <div class="contact-buttons reveal">
            <a href="https://t.me/ponomera2" target="_blank" class="contact-btn"><i class="fab fa-telegram"></i> Telegram</a>
            <a href="mailto:ponomarenkodana410@gmail.com" class="contact-btn"><i class="fas fa-envelope"></i> Email</a>
            <a href="/contact" class="contact-btn"><i class="fas fa-paper-plane"></i> Оставить заявку</a>
        </div>
    </div>
</section>

<footer>
    <p>© 2026 ДАНИИЛ · ВЕБ-РАЗРАБОТЧИК</p>
    <div class="footer-links">
        <a href="/">Главная</a>
        <a href="/services">Услуги</a>
        <a href="/portfolio">Портфолио</a>
        <a href="/pricing">Цены</a>
        <a href="/blog">Блог</a>
        <a href="/contact">Контакты</a>
        <a href="/admin">Админ</a>
    </div>
</footer>

<script>
// Анимации при скролле
document.addEventListener('DOMContentLoaded', function() {
    const reveals = document.querySelectorAll('.reveal');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, { threshold: 0.1 });
    
    reveals.forEach(el => observer.observe(el));
});
function toggleMenu() {
    document.getElementById('navLinks').classList.toggle('active');
    document.querySelector('.burger').classList.toggle('active');
}
function setTheme(theme) {
    document.body.className = '';
    document.body.classList.add('theme-' + theme);
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === theme);
    });
    localStorage.setItem('site-theme', theme);
}
const savedTheme = localStorage.getItem('site-theme') || 'light';
setTheme(savedTheme);

function toggleFaq(el) { el.classList.toggle('active'); }

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
CALCULATOR_HTML = '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Калькулятор стоимости — Даниил</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Inter', sans-serif;
    background: #faf8f5;
    color: #2a2a2a;
    line-height: 1.6;
    min-height: 100vh;
}
.page-header {
    background: linear-gradient(180deg, #ffffff 0%, #faf8f5 100%);
    padding: 80px 20px 60px;
    text-align: center;
    border-bottom: 1px solid rgba(184,134,11,0.15);
    position: relative;
}
.page-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 50%;
    transform: translateX(-50%);
    width: 200px; height: 1px;
    background: linear-gradient(90deg, transparent, #b8860b, transparent);
}
.back-link {
    position: absolute;
    top: 30px; left: 30px;
    color: #b8860b;
    text-decoration: none;
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 500;
}
.top-label {
    font-size: 11px;
    letter-spacing: 6px;
    color: #b8860b;
    text-transform: uppercase;
    margin-bottom: 20px;
    font-weight: 600;
}
h1 {
    font-family: 'Playfair Display', serif;
    font-size: 64px;
    font-weight: 400;
    letter-spacing: -2px;
    color: #2a2a2a;
    margin-bottom: 15px;
}
h1 span { color: #b8860b; font-style: italic; }
.subtitle {
    color: #6b6b6b;
    font-size: 18px;
    max-width: 600px;
    margin: 0 auto;
}

.container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 60px 30px;
}

.calculator {
    background: white;
    border-radius: 12px;
    padding: 50px;
    box-shadow: 0 10px 40px rgba(184,134,11,0.08);
    border: 1px solid rgba(184,134,11,0.1);
}

.calc-title {
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    margin-bottom: 30px;
    color: #2a2a2a;
}

.service-option {
    display: flex;
    align-items: center;
    padding: 20px 25px;
    margin-bottom: 12px;
    border: 2px solid #e8e4dd;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
    user-select: none;
}
.service-option:hover {
    border-color: #b8860b;
    background: #fdfbf7;
}
.service-option.selected {
    border-color: #b8860b;
    background: linear-gradient(135deg, #fef9f0, #fdf4e3);
    box-shadow: 0 5px 20px rgba(184,134,11,0.15);
}
.service-option input[type="checkbox"] {
    appearance: none;
    -webkit-appearance: none;
    width: 24px;
    height: 24px;
    border: 2px solid #b8860b;
    border-radius: 6px;
    margin-right: 20px;
    cursor: pointer;
    position: relative;
    flex-shrink: 0;
    transition: 0.3s;
}
.service-option input[type="checkbox"]:checked {
    background: #b8860b;
}
.service-option input[type="checkbox"]:checked::after {
    content: '✓';
    position: absolute;
    color: white;
    font-size: 16px;
    font-weight: bold;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}
.service-info {
    flex: 1;
}
.service-name {
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    font-weight: 500;
    color: #2a2a2a;
    margin-bottom: 5px;
}
.service-desc {
    color: #6b6b6b;
    font-size: 14px;
}
.service-price {
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    color: #b8860b;
    font-weight: 500;
    margin-left: 20px;
    white-space: nowrap;
}

.total-box {
    margin-top: 40px;
    padding: 40px;
    background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
    border-radius: 12px;
    text-align: center;
    color: white;
}
.total-label {
    font-size: 12px;
    letter-spacing: 4px;
    color: #d4a017;
    text-transform: uppercase;
    margin-bottom: 15px;
}
.total-price {
    font-family: 'Playfair Display', serif;
    font-size: 64px;
    color: #d4a017;
    font-weight: 500;
    line-height: 1;
    margin-bottom: 10px;
}
.total-note {
    color: #999;
    font-size: 13px;
}

.actions {
    display: flex;
    gap: 15px;
    margin-top: 30px;
    flex-wrap: wrap;
    justify-content: center;
}
.btn-gold {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 18px 40px;
    background: #b8860b;
    color: white;
    text-decoration: none;
    font-size: 13px;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-weight: 500;
    transition: 0.3s;
    border-radius: 4px;
    border: none;
    cursor: pointer;
    font-family: 'Inter', sans-serif;
}
.btn-gold:hover {
    background: #d4a017;
    transform: translateY(-3px);
    box-shadow: 0 15px 30px rgba(184,134,11,0.4);
}
.btn-outline {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 18px 40px;
    background: transparent;
    color: #b8860b;
    border: 1px solid #b8860b;
    text-decoration: none;
    font-size: 13px;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-weight: 500;
    transition: 0.3s;
    border-radius: 4px;
    cursor: pointer;
    font-family: 'Inter', sans-serif;
}
.btn-outline:hover {
    background: #b8860b;
    color: white;
}

@media (max-width: 768px) {
    h1 { font-size: 42px; }
    .calculator { padding: 25px; }
    .service-option { padding: 15px; flex-wrap: wrap; }
    .service-price { margin-left: 0; margin-top: 10px; width: 100%; }
    .total-price { font-size: 42px; }
    .calc-title { font-size: 24px; }
}
</style>
</head>
<body>

<div class="page-header">
    <a href="/" class="back-link">← Главная</a>
    <div class="top-label">Даниил · Веб-разработчик</div>
    <h1>Калькулятор <span>стоимости</span></h1>
    <p class="subtitle">Выберите нужные услуги — узнайте стоимость сразу</p>
</div>

<div class="container">
    <div class="calculator">
        <h2 class="calc-title">Что вам нужно?</h2>

        <label class="service-option" onclick="toggleService(this)">
            <input type="checkbox" data-price="5000" data-name="Лендинг">
            <div class="service-info">
                <div class="service-name">Лендинг</div>
                <div class="service-desc">Одностраничный сайт с формой заявки</div>
            </div>
            <div class="service-price">5 000 ₽</div>
        </label>

        <label class="service-option" onclick="toggleService(this)">
            <input type="checkbox" data-price="5000" data-name="Дополнительные страницы">
            <div class="service-info">
                <div class="service-name">Дополнительные страницы</div>
                <div class="service-desc">О нас, Услуги, Портфолио (+5 000 ₽)</div>
            </div>
            <div class="service-price">5 000 ₽</div>
        </label>

        <label class="service-option" onclick="toggleService(this)">
            <input type="checkbox" data-price="5000" data-name="Админ-панель">
            <div class="service-info">
                <div class="service-name">Админ-панель</div>
                <div class="service-desc">Управление заявками и контентом</div>
            </div>
            <div class="service-price">5 000 ₽</div>
        </label>

        <label class="service-option" onclick="toggleService(this)">
            <input type="checkbox" data-price="3000" data-name="Премиум-дизайн">
            <div class="service-info">
                <div class="service-name">Премиум-дизайн</div>
                <div class="service-desc">Анимации, 4 темы, эффекты</div>
            </div>
            <div class="service-price">3 000 ₽</div>
        </label>

        <label class="service-option" onclick="toggleService(this)">
            <input type="checkbox" data-price="8000" data-name="Telegram-бот">
            <div class="service-info">
                <div class="service-name">Telegram-бот</div>
                <div class="service-desc">Приём заявок и уведомления</div>
            </div>
            <div class="service-price">8 000 ₽</div>
        </label>

        <label class="service-option" onclick="toggleService(this)">
            <input type="checkbox" data-price="5000" data-name="Наполнение контентом">
            <div class="service-info">
                <div class="service-name">Наполнение контентом</div>
                <div class="service-desc">Тексты, фото, структура</div>
            </div>
            <div class="service-price">5 000 ₽</div>
        </label>

        <label class="service-option" onclick="toggleService(this)">
            <input type="checkbox" data-price="3000" data-name="SEO-оптимизация">
            <div class="service-info">
                <div class="service-name">SEO-оптимизация</div>
                <div class="service-desc">Настройка для поиска в Яндексе</div>
            </div>
            <div class="service-price">3 000 ₽</div>
        </label>

        <div class="total-box">
            <div class="total-label">Итого</div>
            <div class="total-price"><span id="total">0</span> ₽</div>
            <div class="total-note">Точная цена — после обсуждения задачи</div>
        </div>

        <div class="actions">
            <a href="/contact" class="btn-gold"><i class="fas fa-paper-plane"></i> Оставить заявку</a>
            <a href="https://t.me/ponomera2" target="_blank" class="btn-outline"><i class="fab fa-telegram"></i> Написать в Telegram</a>
        </div>
    </div>
</div>

<script>
function toggleService(el) {
    setTimeout(updateTotal, 10);
}

function updateTotal() {
    const checkboxes = document.querySelectorAll('.service-option input[type="checkbox"]');
    let total = 0;
    checkboxes.forEach(cb => {
        if (cb.checked) {
            total += parseInt(cb.dataset.price);
            cb.closest('.service-option').classList.add('selected');
        } else {
            cb.closest('.service-option').classList.remove('selected');
        }
    });
    document.getElementById('total').textContent = total.toLocaleString('ru-RU');
}

// Инициализация
document.addEventListener('DOMContentLoaded', updateTotal);
</script>

</body>
</html>
'''
SERVICES_HTML = '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Услуги — Даниил</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Inter', sans-serif;
    background: #faf8f5;
    color: #2a2a2a;
    line-height: 1.6;
}

/* Шапка */
.page-header {
    background: linear-gradient(180deg, #ffffff 0%, #faf8f5 100%);
    padding: 80px 20px 60px;
    text-align: center;
    border-bottom: 1px solid rgba(184,134,11,0.15);
    position: relative;
}
.page-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 50%;
    transform: translateX(-50%);
    width: 200px; height: 1px;
    background: linear-gradient(90deg, transparent, #b8860b, transparent);
}
.back-link {
    position: absolute;
    top: 30px; left: 30px;
    color: #b8860b;
    text-decoration: none;
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 500;
    transition: 0.3s;
}
.back-link:hover { color: #d4a017; }
.top-label {
    font-size: 11px;
    letter-spacing: 6px;
    color: #b8860b;
    text-transform: uppercase;
    margin-bottom: 20px;
    font-weight: 600;
}
h1 {
    font-family: 'Playfair Display', serif;
    font-size: 72px;
    font-weight: 400;
    letter-spacing: -2px;
    color: #2a2a2a;
    margin-bottom: 15px;
}
h1 span { color: #b8860b; font-style: italic; }
.subtitle {
    color: #6b6b6b;
    font-size: 18px;
    max-width: 600px;
    margin: 0 auto;
}

/* Секции услуг */
.container { max-width: 1100px; margin: 0 auto; padding: 0 30px; }

.service-block {
    padding: 80px 0;
    border-bottom: 1px solid rgba(184,134,11,0.1);
    display: grid;
    grid-template-columns: 80px 1fr;
    gap: 40px;
    align-items: start;
}
.service-block:last-child { border-bottom: none; }

.service-num {
    font-family: 'Playfair Display', serif;
    font-size: 48px;
    color: #b8860b;
    opacity: 0.4;
    line-height: 1;
    font-style: italic;
}
.service-content h2 {
    font-family: 'Playfair Display', serif;
    font-size: 40px;
    font-weight: 400;
    margin-bottom: 20px;
    color: #2a2a2a;
}
.service-content h2 i {
    color: #b8860b;
    font-size: 32px;
    margin-right: 15px;
}
.service-content > p {
    color: #6b6b6b;
    font-size: 17px;
    margin-bottom: 30px;
    max-width: 700px;
}
.features-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 15px;
    margin: 25px 0;
}
.feature-item {
    padding: 15px 0;
    color: #2a2a2a;
    font-size: 15px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.feature-item i {
    color: #b8860b;
    font-size: 14px;
}

.service-price {
    display: inline-block;
    margin-top: 20px;
    padding: 15px 30px;
    background: #1a1a1a;
    color: #d4a017;
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    font-weight: 500;
    border-radius: 4px;
}
.service-price small {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    color: #999;
    display: block;
    letter-spacing: 2px;
    margin-top: 5px;
    font-weight: 400;
}

/* CTA */
.cta {
    background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
    padding: 80px 20px;
    text-align: center;
    color: white;
    margin-top: 40px;
}
.cta h2 {
    font-family: 'Playfair Display', serif;
    font-size: 44px;
    font-weight: 400;
    margin-bottom: 15px;
}
.cta h2 span { color: #d4a017; font-style: italic; }
.cta p {
    color: #b0b0b0;
    font-size: 16px;
    margin-bottom: 35px;
}
.cta-buttons {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
}
.btn-gold {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 18px 40px;
    background: #b8860b;
    color: white;
    text-decoration: none;
    font-size: 13px;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-weight: 500;
    transition: 0.3s;
    border-radius: 4px;
}
.btn-gold:hover {
    background: #d4a017;
    transform: translateY(-3px);
    box-shadow: 0 15px 30px rgba(184,134,11,0.4);
}
.btn-outline {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 18px 40px;
    background: transparent;
    color: #d4a017;
    border: 1px solid #b8860b;
    text-decoration: none;
    font-size: 13px;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-weight: 500;
    transition: 0.3s;
    border-radius: 4px;
}
.btn-outline:hover {
    background: #b8860b;
    color: white;
}

/* Footer */
footer {
    background: #1a1a1a;
    padding: 40px;
    text-align: center;
    color: #999;
    font-size: 13px;
    letter-spacing: 2px;
}

@media (max-width: 768px) {
    h1 { font-size: 48px; }
    .service-block { grid-template-columns: 1fr; gap: 20px; padding: 50px 0; }
    .service-num { font-size: 32px; }
    .service-content h2 { font-size: 30px; }
    .cta h2 { font-size: 32px; }
}
</style>
</head>
<body>

<div class="page-header">
    <a href="/" class="back-link">← Главная</a>
    <div class="top-label">Даниил · Веб-разработчик</div>
    <h1>Мои <span>услуги</span></h1>
    <p class="subtitle">Полный спектр услуг по созданию сайтов, ботов и веб-приложений</p>
</div>

<div class="container">

    <!-- Услуга 1 -->
    <div class="service-block">
        <div class="service-num">01</div>
        <div class="service-content">
            <h2><i class="fas fa-code"></i> Сайты на Python</h2>
            <p>Создаю современные сайты на Flask: от простых лендингов до многостраничных корпоративных сайтов с админ-панелью и базой данных.</p>
            <div class="features-list">
                <div class="feature-item"><i class="fas fa-check"></i> Лендинги и визитки</div>
                <div class="feature-item"><i class="fas fa-check"></i> Корпоративные сайты</div>
                <div class="feature-item"><i class="fas fa-check"></i> Админ-панель для управления</div>
                <div class="feature-item"><i class="fas fa-check"></i> База данных (SQLite/PostgreSQL)</div>
                <div class="feature-item"><i class="fas fa-check"></i> Адаптив под телефон</div>
                <div class="feature-item"><i class="fas fa-check"></i> Форма заявок с уведомлениями</div>
            </div>
            <div class="service-price">
                от 5 000 ₽
                <small>СРОК: 2-7 ДНЕЙ</small>
            </div>
        </div>
    </div>

    <!-- Услуга 2 -->
    <div class="service-block">
        <div class="service-num">02</div>
        <div class="service-content">
            <h2><i class="fas fa-robot"></i> Telegram-боты</h2>
            <p>Разрабатываю ботов для бизнеса: приём заявок, автоматизация, рассылки, уведомления. Бот поможет автоматизировать рутинные задачи.</p>
            <div class="features-list">
                <div class="feature-item"><i class="fas fa-check"></i> Боты для продаж</div>
                <div class="feature-item"><i class="fas fa-check"></i> Приём заявок и уведомления</div>
                <div class="feature-item"><i class="fas fa-check"></i> Боты-помощники (AI)</div>
                <div class="feature-item"><i class="fas fa-check"></i> Интеграция с сайтом</div>
                <div class="feature-item"><i class="fas fa-check"></i> Автоматизация рассылок</div>
                <div class="feature-item"><i class="fas fa-check"></i> Оплата прямо в боте</div>
            </div>
            <div class="service-price">
                от 8 000 ₽
                <small>СРОК: 3-5 ДНЕЙ</small>
            </div>
        </div>
    </div>

    <!-- Услуга 3 -->
    <div class="service-block">
        <div class="service-num">03</div>
        <div class="service-content">
            <h2><i class="fas fa-gem"></i> Премиум-дизайн</h2>
            <p>Элегантный дизайн в стиле люксовых брендов: бело-золотые оттенки, плавные анимации, дорогой вид. Ваш сайт будет выделяться.</p>
            <div class="features-list">
                <div class="feature-item"><i class="fas fa-check"></i> Индивидуальный дизайн</div>
                <div class="feature-item"><i class="fas fa-check"></i> Анимации и эффекты</div>
                <div class="feature-item"><i class="fas fa-check"></i> Переключение тем</div>
                <div class="feature-item"><i class="fas fa-check"></i> Премиум-шрифты</div>
                <div class="feature-item"><i class="fas fa-check"></i> Скруглённые углы и тени</div>
                <div class="feature-item"><i class="fas fa-check"></i> Glassmorphism эффекты</div>
            </div>
            <div class="service-price">
                от 5 000 ₽
                <small>ВХОДИТ В САЙТ</small>
            </div>
        </div>
    </div>

    <!-- Услуга 4 -->
    <div class="service-block">
        <div class="service-num">04</div>
        <div class="service-content">
            <h2><i class="fas fa-database"></i> Веб-приложения</h2>
            <p>Создаю сложные веб-приложения: CRM-системы, личные кабинеты, дашборды с аналитикой и графиками.</p>
            <div class="features-list">
                <div class="feature-item"><i class="fas fa-check"></i> CRM-системы</div>
                <div class="feature-item"><i class="fas fa-check"></i> Личные кабинеты</div>
                <div class="feature-item"><i class="fas fa-check"></i> Дашборды с графиками</div>
                <div class="feature-item"><i class="fas fa-check"></i> Регистрация и вход</div>
                <div class="feature-item"><i class="fas fa-check"></i> Экспорт в Excel/CSV</div>
                <div class="feature-item"><i class="fas fa-check"></i> Роли пользователей</div>
            </div>
            <div class="service-price">
                от 20 000 ₽
                <small>СРОК: 10-14 ДНЕЙ</small>
            </div>
        </div>
    </div>

</div>

<!-- CTA -->
<section class="cta">
    <h2>Готовы <span>начать?</span></h2>
    <p>Обсудим вашу задачу — предложу лучшее решение</p>
    <div class="cta-buttons">
        <a href="https://t.me/ponomera2" target="_blank" class="btn-gold">
            <i class="fab fa-telegram"></i> Telegram
        </a>
        <a href="/contact" class="btn-outline">
            <i class="fas fa-paper-plane"></i> Оставить заявку
        </a>
    </div>
</section>

<footer>
    © 2026 ДАНИИЛ · ВЕБ-РАЗРАБОТЧИК
</footer>

</body>
</html>
'''
PRICING_HTML = '''<!DOCTYPE html><html><head><title>Цены</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0f1a;color:#fff;font-family:Segoe UI,Arial,sans-serif;padding:40px 20px}.container{max-width:1100px;margin:0 auto;text-align:center}h1{font-size:42px;margin-bottom:15px}.sub{color:#aaa;margin-bottom:40px}.pricing{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:25px;text-align:left}.price-card{background:rgba(255,255,255,0.05);padding:35px;border-radius:25px;border:1px solid rgba(255,255,255,0.08);transition:0.4s;position:relative}.price-card:hover{transform:translateY(-10px);border-color:#6c63ff}.price-card.popular::before{content:'ПОПУЛЯРНЫЙ';position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:#ff6b6b;padding:4px 15px;border-radius:20px;font-size:11px;font-weight:700}.price-card h3{font-size:24px;margin-bottom:10px}.price-card .price{font-size:42px;color:#6c63ff;font-weight:700;margin:15px 0}.price-card ul{list-style:none;margin:20px 0}.price-card li{padding:8px 0;color:#ccc}.price-card li i{color:#22c55e;margin-right:10px}.btn{display:inline-block;background:linear-gradient(135deg,#6c63ff,#ff6b6b);color:#fff;padding:14px 30px;border-radius:50px;text-decoration:none;font-weight:700;width:100%;text-align:center;margin-top:15px}a{color:#6c63ff;text-decoration:none;display:block;margin-top:30px;text-align:center}</style></head><body><div class="container"><h1>💰 Цены</h1><p class="sub">Прозрачные цены без скрытых платежей</p><div class="pricing"><div class="price-card"><h3>Лендинг</h3><div class="price">5 000 ₽</div><ul><li><i class="fas fa-check"></i>Одностраничный сайт</li><li><i class="fas fa-check"></i>Адаптивный дизайн</li><li><i class="fas fa-check"></i>Форма заявки</li></ul><a href="/contact" class="btn">Заказать</a></div><div class="price-card popular"><h3>Сайт + Админка</h3><div class="price">15 000 ₽</div><ul><li><i class="fas fa-check"></i>Многостраничный</li><li><i class="fas fa-check"></i>Админ-панель</li><li><i class="fas fa-check"></i>База данных</li></ul><a href="/contact" class="btn">Заказать</a></div><div class="price-card"><h3>Сайт + Бот</h3><div class="price">25 000 ₽</div><ul><li><i class="fas fa-check"></i>Всё из «+ Админка»</li><li><i class="fas fa-check"></i>Telegram-бот</li><li><i class="fas fa-check"></i>Уведомления</li></ul><a href="/contact" class="btn">Заказать</a></div></div><a href="/">← На главную</a></div></body></html>'''

BLOG_HTML = '''<!DOCTYPE html><html><head><title>Блог</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0f1a;color:#fff;font-family:Segoe UI,Arial,sans-serif;padding:40px 20px}.container{max-width:900px;margin:0 auto}.card{background:rgba(255,255,255,0.05);padding:40px;border-radius:25px;border:1px solid rgba(255,255,255,0.08)}h1{text-align:center}.post{border-bottom:1px solid rgba(255,255,255,0.06);padding:20px 0}.post:last-child{border-bottom:none}.post small{color:#666}.post p{color:#aaa}a{color:#6c63ff;text-decoration:none;display:block;margin-top:20px;text-align:center}</style></head><body><div class="container"><div class="card"><h1>📝 Блог</h1>{% for post in posts %}<div class="post"><h3>{{ post[1] }}</h3><small>{{ post[3] }}</small><p>{{ post[2][:200] }}...</p><a href="/post/{{ post[0] }}">Читать →</a></div>{% endfor %}{% if posts|length==0 %}<p>Нет записей</p>{% endif %}<a href="/">← На главную</a></div></div></body></html>'''

POST_HTML = '''<!DOCTYPE html><html><head><title>Статья</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0f1a;color:#fff;font-family:Segoe UI,Arial,sans-serif;padding:40px 20px}.container{max-width:800px;margin:0 auto}.card{background:rgba(255,255,255,0.05);padding:40px;border-radius:25px;border:1px solid rgba(255,255,255,0.08)}h1{color:#fff}small{color:#666;display:block;margin:10px 0}p{color:#aaa;line-height:1.8}.btn{display:inline-block;background:#6c63ff;color:#fff;padding:10px 25px;border-radius:20px;text-decoration:none;margin-top:20px}</style></head><body><div class="container"><div class="card"><h1>{{ post[1] }}</h1><small>{{ post[3] }}</small><p>{{ post[2] }}</p><a href="/blog" class="btn">Все записи</a></div></div></body></html>'''

CONTACT_HTML = '''<!DOCTYPE html><html><head><title>Контакты</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0f1a;color:#fff;font-family:Segoe UI,Arial,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px}.card{background:rgba(255,255,255,0.05);padding:40px;border-radius:30px;border:1px solid rgba(255,255,255,0.08);max-width:500px;width:100%}h1{text-align:center;margin-bottom:20px}h1 i{color:#6c63ff}input,textarea{width:100%;padding:14px;margin:10px 0;border-radius:12px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:#fff;font-size:16px}input:focus,textarea:focus{outline:none;border-color:#6c63ff}button{width:100%;padding:15px;border-radius:12px;border:none;background:linear-gradient(135deg,#6c63ff,#ff6b6b);color:#fff;font-size:18px;font-weight:600;cursor:pointer}a{color:#6c63ff;text-decoration:none;display:inline-block;margin-top:15px}</style></head><body><div class="card"><h1><i class="fas fa-paper-plane"></i> Напиши мне</h1><form method="POST"><input type="text" name="name" placeholder="Имя" required><input type="text" name="phone" placeholder="Телефон" required><textarea name="message" rows="5" placeholder="Сообщение" required></textarea><button type="submit">Отправить</button></form><a href="/">На главную</a></div></body></html>'''

SUCCESS_HTML = '''<!DOCTYPE html><html><head><title>Спасибо!</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0f1a;color:#fff;font-family:Segoe UI,Arial,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;padding:20px}.card{background:rgba(255,255,255,0.05);padding:50px;border-radius:30px;text-align:center;border:1px solid rgba(255,255,255,0.08);max-width:500px;width:100%}.card i{font-size:80px;color:#22c55e}h1{color:#fff}a{color:#6c63ff;text-decoration:none;font-weight:600}</style></head><body><div class="card"><i class="fas fa-check-circle"></i><h1>✅ Спасибо, {{ name }}!</h1><p>Ваша заявка принята.</p><br><a href="/">На главную</a></div></body></html>'''


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

@app.route('/services')
def services():
    return render_template_string(SERVICES_HTML)

@app.route('/calculator')
def calculator():
    return render_template_string(CALCULATOR_HTML)

@app.route('/robots.txt')
def robots():
    """Правила для поисковых роботов"""
    txt = "User-agent: *\n"
    txt += "Allow: /\n"
    txt += "Disallow: /admin\n"
    txt += "Disallow: /admin/\n"
    txt += "Disallow: /login\n"
    txt += "Disallow: /logout\n"
    txt += "\n"
    txt += "Sitemap: https://my-flask-site-sext.onrender.com/sitemap.xml\n"
    return txt, 200, {'Content-Type': 'text/plain'}

@app.route('/sitemap.xml')
def sitemap():
    """Карта сайта для поисковых систем"""
    pages = [
        ('/', '1.0', 'weekly'),
        ('/services', '0.9', 'monthly'),
        ('/portfolio', '0.9', 'weekly'),
        ('/pricing', '0.8', 'monthly'),
        ('/calculator', '0.8', 'monthly'),
        ('/blog', '0.7', 'weekly'),
        ('/contact', '0.7', 'monthly'),
        ('/chat', '0.5', 'monthly'),
    ]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url, priority, freq in pages:
        xml += f'  <url>\n'
        xml += f'    <loc>https://my-flask-site-sext.onrender.com{url}</loc>\n'
        xml += f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
        xml += f'    <changefreq>{freq}</changefreq>\n'
        xml += f'    <priority>{priority}</priority>\n'
        xml += f'  </url>\n'
    xml += '</urlset>'
    return xml, 200, {'Content-Type': 'application/xml'}



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
# ===== АДМИН: ДАШБОРД =====
@app.route('/admin')
@login_required
def admin():
    messages = get_messages()
    today = datetime.now().strftime('%Y-%m-%d')

    today_count = sum(1 for m in messages if m[4] and m[4].startswith(today))
    week_count = len(messages)

    chart_data = [0, 0, 0, 0, 0, 0, 0]
    for m in messages:
        if m[4]:
            try:
                msg_date = m[4][:10]
                delta = (datetime.now() - datetime.strptime(msg_date, '%Y-%m-%d')).days
                if 0 <= delta <= 6:
                    chart_data[6 - delta] += 1
            except:
                pass

        return render_template_string(
        ADMIN_HTML,
        count=get_count(),
        posts_count=len(get_posts()),
        today_count=today_count,
        week_count=week_count,
        chart_data=chart_data
    )

# ===== АДМИН: ЗАЯВКИ =====
@app.route('/admin/messages')
@login_required
def admin_messages():
    search = request.args.get('search', '')
    return render_template_string(
        ADMIN_MESSAGES_HTML,
        messages=get_messages(search),
        count=get_count(),
        search=search
    )


# ===== АДМИН: БЛОГ =====
@app.route('/admin/blog')
@login_required
def admin_blog():
    return render_template_string(
        ADMIN_BLOG_HTML,
        posts=get_posts()
    )


# ===== АДМИН: УДАЛЕНИЕ ЗАЯВКИ =====
@app.route('/admin/delete/<int:msg_id>')
@login_required
def admin_delete(msg_id):
    delete_message(msg_id)
    return redirect('/admin/messages')


# ===== АДМИН: ДОБАВЛЕНИЕ СТАТЬИ =====
@app.route('/admin/add_post', methods=['POST'])
@login_required
def add_post_route():
    title = request.form['title']
    content = request.form['content']
    add_post(title, content)
    return redirect('/admin/blog')



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








    
    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';')
    
    writer.writerow(['ID', 'Имя', 'Телефон', 'Сообщение', 'Дата'])
    
    for msg in messages:
        writer.writerow([msg[0], msg[1], msg[2], msg[3], msg[4]])
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=zayavki_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.csv'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    
    return response



@app.route('/chat')
def chat():
    return render_template_string(CHAT_HTML)


@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    q = data.get('question', '').lower().strip()
    
    # ===== ПРИВЕТСТВИЕ =====
    if any(w in q for w in ['привет', 'здравствуй', 'хай', 'hi', 'hello', 'добрый']):
        answer = random.choice([
            'Привет! Как дела? 😊',
            'Здравствуй! Рад тебя видеть! 👋',
            'Хэй! Давно не виделись! 🤗',
            'Привет-привет! Чем могу помочь? 💪',
            'Добрый день! Что тебя интересует? 😊'
        ])
    
    elif any(w in q for w in ['как дела', 'как жизнь', 'как ты', 'как сам']):
        answer = random.choice([
            'У меня всё отлично! А у тебя? 😄',
            'Супер! Программирую и радуюсь! 🚀',
            'Лучше всех! Ты как? 😎',
            'Отлично! Жду твоих вопросов! 🤖',
            'Всё хорошо! Спасибо, что спросил! ✨'
        ])
    
    # ===== ИМЯ =====
    elif any(w in q for w in ['имя', 'зовут', 'как тебя']):
        answer = random.choice([
            'Меня зовут Бот-помощник! 🤖',
            'Я — твой виртуальный друг! Зови меня Бот! 😄',
            'Моё имя — Бот! Приятно познакомиться! 👋'
        ])
    
    # ===== ПРОГРАММИРОВАНИЕ =====
    elif any(w in q for w in ['python', 'питон']):
        answer = random.choice([
            'Python — крутой язык программирования! 🐍',
            'На Python можно делать сайты, ботов, нейросети! 💻',
            'Python — самый популярный язык для начинающих! 🔥',
            'Сам использую Python для проектов! 🚀'
        ])
    
    elif any(w in q for w in ['flask', 'фласк']):
        answer = 'Этот сайт сделан на Flask — микрофреймворке Python! 🔥 Хочешь такой же?'
    
    elif any(w in q for w in ['бот', 'telegram', 'телеграм']):
        answer = random.choice([
            'Умею создавать Telegram-ботов! 🤖',
            'Боты — это моя страсть! Могу для тебя сделать! 🔥',
            'Telegram-боты — круто! Автоматизация бизнеса! 💪',
            'Хочешь бота? От 8 000 ₽, срок 3-5 дней! 📱'
        ])
    
    # ===== УСЛУГИ =====
    elif any(w in q for w in ['сайт', 'лендинг', 'визитка']):
        answer = random.choice([
            'Создаю современные сайты на Python! 🔥',
            'Лендинг — от 5 000 ₽. Сайт с админкой — от 15 000 ₽. 🚀',
            'Хочешь сайт? Обсудим! Напиши на /contact 💪',
            'Делаю премиум-сайты с анимациями и админкой! ✨'
        ])
    
    elif any(w in q for w in ['бот', 'боты', 'автоматизация']):
        answer = 'Telegram-боты для бизнеса: приём заявок, рассылки, уведомления! От 8 000 ₽. 🤖'
    
    elif any(w in q for w in ['дизайн', 'красиво', 'стиль']):
        answer = 'Делаю премиум-дизайн: анимации, градиенты, 4 темы! 🎨'
    
    # ===== ЦЕНЫ =====
    elif any(w in q for w in ['цена', 'цены', 'стоит', 'стоимость', 'сколько']):
        answer = random.choice([
            '💰 Лендинг — 5 000 ₽\n💰 Сайт + Админка — 15 000 ₽\n💰 Сайт + Бот — 25 000 ₽\n\nПодробнее: /pricing',
            'Цены: лендинг 5 000 ₽, сайт с админкой 15 000 ₽, сайт с ботом 25 000 ₽ 💰',
            'Лендинг — от 5 000 ₽. Хочешь калькулятор? /calculator 💰'
        ])
    
    elif any(w in q for w in ['скидк', 'дешев', 'дорого', 'бюджет']):
        answer = random.choice([
            'Есть лендинг за 5 000 ₽ — бюджетный вариант! 💰',
            'Можем обсудить цену под твой бюджет! Напиши /contact 💬',
            'Для новых клиентов — скидка 10%! 🔥'
        ])
    
    elif any(w in q for w in ['срок', 'время', 'быстро', 'когда']):
        answer = 'Лендинг — 2-3 дня. Сайт с админкой — 5-7 дней. Сайт с ботом — 7-10 дней. ⏰'
    
    # ===== ПОРТФОЛИО =====
    elif any(w in q for w in ['работы', 'портфолио', 'примеры', 'проекты']):
        answer = 'Посмотри мои работы: /portfolio 💼 Делал сайты для SPA, косметологии, клиник! ✨'
    
    elif any(w in q for w in ['отзыв', 'клиент', 'нравится']):
        answer = 'Клиенты довольны! Посмотри отзывы на главной странице ⭐'
    
    # ===== КОНТАКТЫ =====
    elif any(w in q for w in ['контакт', 'связ', 'написать', 'найти']):
        answer = '📱 Telegram: @ponomera2\n📧 Email: ponomarenkodana410@gmail.com\n\nИли /contact 📩'
    
    elif any(w in q for w in ['telegram', 'телеграм', 'tg', 'тг']):
        answer = 'Мой Telegram: @ponomera2 — пиши, отвечу быстро! 📱'
    
    elif any(w in q for w in ['email', 'почта', 'мейл', 'mail']):
        answer = 'Мой Email: ponomarenkodana410@gmail.com 📧'
    
    elif any(w in q for w in ['телефон', 'позвон', 'номер']):
        answer = 'Лучше пиши в Telegram: @ponomera2 — отвечу быстрее! 📱'
    
    # ===== ЗАКАЗ =====
    elif any(w in q for w in ['заказ', 'хочу сайт', 'нужен сайт', 'сделай']):
        answer = random.choice([
            'Отлично! Напиши мне в Telegram: @ponomera2 📱',
            'Круто! Оставь заявку: /contact — свяжусь с тобой 💪',
            'Обсудим! Telegram: @ponomera2 🚀'
        ])
    
    elif any(w in q for w in ['оплат', 'предоплат', 'деньги']):
        answer = 'Оплата: 50% предоплата, 50% после сдачи. Работаю по договору! 💰'
    
    elif any(w in q for w in ['гарант', 'обман', 'кидал']):
        answer = 'Даю гарантию месяц на все работы! Если что-то сломается — исправлю бесплатно! ✅'
    
    # ===== ПОМОЩЬ =====
    elif any(w in q for w in ['помощь', 'помог', 'подскаж', 'совет']):
        answer = 'Конечно помогу! Спроси о чём угодно: о сайтах, ботах, ценах, услугах! 😊'
    
    elif any(w in q for w in ['что умеешь', 'что можешь', 'функции']):
        answer = 'Умею: делать сайты, создавать ботов, работать с Python, HTML, CSS, базами данных! 💻'
    
    elif any(w in q for w in ['учит', 'обуча', 'курс', 'научи']):
        answer = 'Хочешь научиться программировать? Могу подсказать с чего начать! Спроси! 📚'
    
    # ===== ШУТКИ =====
    elif any(w in q for w in ['шутк', 'анекдот', 'смешн']):
        answer = random.choice([
            'Почему программисты не любят природу? Потому что там много багов! 😂',
            'Программист — это человек, который решает проблему, которой у вас не было! 🤓',
            'Сколько программистов нужно для замены лампочки? Ни одного — это проблема железа! 💡',
            'Программист — это машина по превращению кофе в код! ☕💻',
            'Есть 10 типов людей: те кто понимает двоичный код и те кто не понимает! 😄'
        ])
    
    elif any(w in q for w in ['анекдот', 'смешинк']):
        answer = 'Решил программист пойти в спортзал. Купил абонемент. На следующий день уволился. Не работает! 😂'
    
    # ===== ВРЕМЯ / ПОГОДА =====
    elif any(w in q for w in ['время', 'час', 'сколько времени']):
        answer = f'Сейчас {datetime.now().strftime("%H:%M")} по московскому времени! 🕐'
    
    elif any(w in q for w in ['погод', 'дожд', 'солнц']):
        answer = random.choice([
            'Погода сегодня отличная! 🌤️',
            'На улице солнечно! Иди гулять! ☀️',
            'Не знаю точно, но надеюсь, что тепло! 😄'
        ])
    
    elif 'дата' in q or 'число' in q:
        answer = f'Сегодня {datetime.now().strftime("%d.%m.%Y")} 📅'
    
    # ===== БЛАГОДАРНОСТЬ =====
    elif any(w in q for w in ['спасибо', 'благодар', 'спс', 'спсб']):
        answer = random.choice([
            'Пожалуйста! Рад помочь! 😊',
            'Всегда пожалуйста! Обращайся ещё! 🤗',
            'Не за что! Ты крутой! 💪',
            'Рад был помочь! 🚀'
        ])
    
    # ===== ПРОЩАНИЕ =====
    elif any(w in q for w in ['пока', 'до свид', 'бай', 'прощай']):
        answer = random.choice([
            'Пока! Возвращайся скорее! 👋',
            'До встречи! Буду ждать! 😊',
            'Пока-пока! Удачи во всём! 🚀',
            'До связи! Обращайся, если что! 💪'
        ])
    
    # ===== СЛОЖНЫЕ ВОПРОСЫ =====
    elif any(w in q for w in ['как делаешь', 'как создать', 'как сделать']):
        answer = 'Интересный вопрос! Давай обсудим подробнее в Telegram: @ponomera2 📱'
    
    elif 'почему' in q:
        answer = 'Хороший вопрос! Зависит от конкретной ситуации. Спроси подробнее! 🤔'
    
    elif 'что такое' in q:
        answer = 'Интересный вопрос! Могу рассказать про сайты, ботов и Python! Спроси конкретнее! 💻'
    
    # ===== ДЕФОЛТ =====
    else:
        answer = random.choice([
            'Интересный вопрос! 🤔 Расскажи подробнее.',
            'Хм, я ещё учусь. Но рад помочь! Может спросишь про услуги или цены? 💰',
            'Попробуй спросить про сайты, ботов или цены — я в этом силён! 💻',
            'Ого! Ты меня застал врасплох! Но я стараюсь! 😄',
            'Отличный вопрос! Я запишу его и изучу! 📝',
            'Не уверен, что понял. Спроси про: сайты, боты, цены, услуги, контакты! 📋'
        ])
    
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
# ===== АДМИН: ЗАЯВКИ =====
ADMIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Админ-панель — Даниил</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', sans-serif; background: #faf8f5; color: #2a2a2a; }
.admin-header { background: linear-gradient(135deg, #1a1a1a, #2a2a2a); color: white; padding: 0 40px; height: 70px; display: flex; align-items: center; justify-content: space-between; }
.admin-logo { font-family: 'Playfair Display', serif; font-size: 22px; letter-spacing: 2px; }
.admin-logo span { color: #d4a017; font-style: italic; }
.logout-btn { background: transparent; color: #ff6b6b; border: 1px solid #ff6b6b; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-size: 13px; }
.logout-btn:hover { background: #ff6b6b; color: white; }
.admin-layout { display: flex; min-height: calc(100vh - 70px); }
.sidebar { width: 240px; background: white; border-right: 1px solid rgba(184,134,11,0.15); padding: 30px 0; }
.sidebar a { display: flex; align-items: center; gap: 15px; padding: 15px 30px; color: #6b6b6b; text-decoration: none; font-size: 14px; border-left: 3px solid transparent; }
.sidebar a:hover { background: #fdfbf7; color: #b8860b; }
.sidebar a.active { background: linear-gradient(135deg, #fef9f0, #fdf4e3); color: #b8860b; border-left-color: #b8860b; }
.admin-content { flex: 1; padding: 40px; }
.page-title { font-family: 'Playfair Display', serif; font-size: 36px; margin-bottom: 30px; }
.page-title span { color: #b8860b; font-style: italic; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }
.stat-card { background: white; padding: 30px; border-radius: 12px; border: 1px solid rgba(184,134,11,0.15); }
.stat-card i { font-size: 28px; color: #b8860b; margin-bottom: 15px; display: block; }
.stat-card h3 { font-family: 'Playfair Display', serif; font-size: 42px; margin-bottom: 5px; }
.stat-card p { color: #6b6b6b; font-size: 13px; text-transform: uppercase; }
.chart-card { background: white; padding: 30px; border-radius: 12px; border: 1px solid rgba(184,134,11,0.15); margin-bottom: 40px; }
.chart-card h3 { font-family: 'Playfair Display', serif; font-size: 22px; margin-bottom: 20px; }
.btn-primary { display: inline-flex; align-items: center; gap: 10px; background: #b8860b; color: white; padding: 12px 25px; border-radius: 8px; text-decoration: none; font-size: 13px; border: none; cursor: pointer; }
.btn-primary:hover { background: #d4a017; }
.btn-success { background: #22c55e; }
.btn-success:hover { background: #16a34a; }
</style>
</head>
<body>

<div class="admin-header">
    <div class="admin-logo">ДАНИИЛ <span>· АДМИН</span></div>
    <div><a href="/logout" class="logout-btn"><i class="fas fa-sign-out-alt"></i> Выйти</a></div>
</div>

<div class="admin-layout">
    <div class="sidebar">
        <a href="/admin" class="active"><i class="fas fa-chart-line"></i> Дашборд</a>
        <a href="/admin/messages"><i class="fas fa-envelope"></i> Заявки</a>
        <a href="/admin/blog"><i class="fas fa-blog"></i> Блог</a>
        <a href="/" target="_blank"><i class="fas fa-external-link-alt"></i> На сайт</a>
    </div>

    <div class="admin-content">
        <h1 class="page-title">📊 <span>Дашборд</span></h1>

        <div class="stats-grid">
            <div class="stat-card"><i class="fas fa-envelope"></i><h3>{{ count }}</h3><p>Заявок</p></div>
            <div class="stat-card"><i class="fas fa-blog"></i><h3>{{ posts_count }}</h3><p>Статей</p></div>
            <div class="stat-card"><i class="fas fa-calendar-day"></i><h3>{{ today_count }}</h3><p>Сегодня</p></div>
            <div class="stat-card"><i class="fas fa-fire"></i><h3>{{ week_count }}</h3><p>За неделю</p></div>
        </div>

        <div class="chart-card">
            <h3>📈 Заявки за 7 дней</h3>
            <canvas id="adminChart" height="80"></canvas>
        </div>

        <div class="chart-card">
            <h3>⚡ Быстрые действия</h3>
            <div style="display:flex;gap:15px;flex-wrap:wrap;margin-top:20px">
                <a href="/admin/messages" class="btn-primary"><i class="fas fa-envelope"></i> Все заявки</a>
                <a href="/admin/export" class="btn-primary btn-success"><i class="fas fa-download"></i> Скачать CSV</a>
                <a href="/admin/blog" class="btn-primary"><i class="fas fa-plus"></i> Добавить статью</a>
            </div>
        </div>
    </div>
</div>

<script>
const ctx = document.getElementById('adminChart');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['6д','5д','4д','3д','2д','Вчера','Сегодня'],
        datasets: [{
            label: 'Заявки',
            data: {{ chart_data|safe }},
            borderColor: '#b8860b',
            backgroundColor: 'rgba(184,134,11,0.1)',
            borderWidth: 3,
            tension: 0.4,
            fill: true,
            pointBackgroundColor: '#d4a017',
            pointRadius: 6
        }]
    },
    options: { responsive: true, scales: { y: { beginAtZero: true } } }
});
</script>

</body>
</html>
'''

ADMIN_MESSAGES_HTML = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Заявки — Админ</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', sans-serif; background: #faf8f5; color: #2a2a2a; }
.admin-header { background: linear-gradient(135deg, #1a1a1a, #2a2a2a); color: white; padding: 0 40px; height: 70px; display: flex; align-items: center; justify-content: space-between; }
.admin-logo { font-family: 'Playfair Display', serif; font-size: 22px; letter-spacing: 2px; }
.admin-logo span { color: #d4a017; font-style: italic; }
.admin-user { display: flex; align-items: center; gap: 20px; font-size: 14px; color: #ccc; }
.logout-btn { background: transparent; color: #ff6b6b; border: 1px solid #ff6b6b; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-size: 13px; letter-spacing: 1px; transition: 0.3s; display: inline-flex; align-items: center; gap: 8px; }
.logout-btn:hover { background: #ff6b6b; color: white; }
.admin-layout { display: flex; min-height: calc(100vh - 70px); }
.sidebar { width: 240px; background: white; border-right: 1px solid rgba(184,134,11,0.15); padding: 30px 0; flex-shrink: 0; }
.sidebar a { display: flex; align-items: center; gap: 15px; padding: 15px 30px; color: #6b6b6b; text-decoration: none; font-size: 14px; font-weight: 500; letter-spacing: 1px; transition: 0.3s; border-left: 3px solid transparent; }
.sidebar a:hover { background: #fdfbf7; color: #b8860b; }
.sidebar a.active { background: linear-gradient(135deg, #fef9f0, #fdf4e3); color: #b8860b; border-left-color: #b8860b; }
.sidebar a i { font-size: 18px; width: 20px; }
.admin-content { flex: 1; padding: 40px; overflow-x: auto; }
.page-title { font-family: 'Playfair Display', serif; font-size: 36px; margin-bottom: 30px; }
.page-title span { color: #b8860b; font-style: italic; }
.table-card { background: white; padding: 30px; border-radius: 12px; border: 1px solid rgba(184,134,11,0.15); }
.search-box { display: flex; gap: 10px; margin-bottom: 25px; }
.search-box input { flex: 1; padding: 12px 20px; border: 1px solid rgba(184,134,11,0.3); border-radius: 8px; font-size: 14px; font-family: 'Inter', sans-serif; }
.search-box input:focus { outline: none; border-color: #b8860b; }
.btn-primary { display: inline-flex; align-items: center; gap: 10px; background: #b8860b; color: white; padding: 12px 25px; border-radius: 8px; text-decoration: none; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; font-weight: 500; border: none; cursor: pointer; transition: 0.3s; }
.btn-primary:hover { background: #d4a017; transform: translateY(-2px); box-shadow: 0 10px 25px rgba(184,134,11,0.3); }
.btn-success { background: #22c55e; }
.btn-success:hover { background: #16a34a; }
.btn-green { background: #22c55e; }
.admin-table { width: 100%; border-collapse: collapse; }
.admin-table th { background: linear-gradient(135deg, #1a1a1a, #2a2a2a); color: white; padding: 15px; text-align: left; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; font-weight: 500; }
.admin-table td { padding: 15px; border-bottom: 1px solid rgba(184,134,11,0.1); font-size: 14px; }
.admin-table tr:hover td { background: #fdfbf7; }
.admin-table tr:last-child td { border-bottom: none; }
.delete-btn { color: #ff6b6b; text-decoration: none; font-size: 18px; }
.delete-btn:hover { color: #dc2626; }
.actions-bar { display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }
@media (max-width: 768px) {
    .admin-header { padding: 0 20px; }
    .admin-user span { display: none; }
    .sidebar { width: 70px; }
    .sidebar a { padding: 15px; justify-content: center; }
    .sidebar a span { display: none; }
    .admin-content { padding: 20px; }
    .page-title { font-size: 24px; }
    .admin-table th, .admin-table td { padding: 10px 8px; font-size: 12px; }
}
</style>
</head>
<body>

<div class="admin-header">
    <div class="admin-logo">ДАНИИЛ <span>· АДМИН</span></div>
    <div class="admin-user">
        <span><i class="fas fa-user"></i> Администратор</span>
        <a href="/logout" class="logout-btn"><i class="fas fa-sign-out-alt"></i> Выйти</a>
    </div>
</div>

<div class="admin-layout">
    <div class="sidebar">
        <a href="/admin"><i class="fas fa-chart-line"></i> <span>Дашборд</span></a>
        <a href="/admin/messages" class="active"><i class="fas fa-envelope"></i> <span>Заявки</span></a>
        <a href="/admin/blog"><i class="fas fa-blog"></i> <span>Блог</span></a>
        <a href="/" target="_blank"><i class="fas fa-external-link-alt"></i> <span>На сайт</span></a>
    </div>

    <div class="admin-content">
        <h1 class="page-title">📋 <span>Заявки</span> <span style="background:#b8860b;color:white;padding:5px 15px;border-radius:20px;font-size:16px;font-family:Inter">{{ count }}</span></h1>

        <div class="actions-bar">
            <a href="/admin/export" class="btn-primary btn-green"><i class="fas fa-download"></i> Скачать CSV</a>
        </div>

        <div class="table-card">
            <form method="GET" class="search-box">
                <input type="text" name="search" placeholder="🔍 Поиск по имени, телефону или сообщению..." value="{{ search }}">
                <button type="submit" class="btn-primary"><i class="fas fa-search"></i> Найти</button>
            </form>

            <table class="admin-table">
                <tr>
                    <th>ID</th>
                    <th>Имя</th>
                    <th>Телефон</th>
                    <th>Сообщение</th>
                    <th>Дата</th>
                    <th></th>
                </tr>
                {% for msg in messages %}
                <tr>
                    <td><strong>#{{ msg[0] }}</strong></td>
                    <td>{{ msg[1] }}</td>
                    <td>{{ msg[2] }}</td>
                    <td>{{ msg[3] }}</td>
                    <td>{{ msg[4] }}</td>
                    <td><a href="/admin/delete/{{ msg[0] }}" class="delete-btn" onclick="return confirm('Удалить заявку?')"><i class="fas fa-trash"></i></a></td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</div>

</body>
</html>
'''

# ===== АДМИН: БЛОГ =====
ADMIN_BLOG_HTML = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Блог — Админ</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', sans-serif; background: #faf8f5; color: #2a2a2a; }
.admin-header { background: linear-gradient(135deg, #1a1a1a, #2a2a2a); color: white; padding: 0 40px; height: 70px; display: flex; align-items: center; justify-content: space-between; }
.admin-logo { font-family: 'Playfair Display', serif; font-size: 22px; letter-spacing: 2px; }
.admin-logo span { color: #d4a017; font-style: italic; }
.admin-user { display: flex; align-items: center; gap: 20px; font-size: 14px; color: #ccc; }
.logout-btn { background: transparent; color: #ff6b6b; border: 1px solid #ff6b6b; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-size: 13px; letter-spacing: 1px; transition: 0.3s; display: inline-flex; align-items: center; gap: 8px; }
.logout-btn:hover { background: #ff6b6b; color: white; }
.admin-layout { display: flex; min-height: calc(100vh - 70px); }
.sidebar { width: 240px; background: white; border-right: 1px solid rgba(184,134,11,0.15); padding: 30px 0; flex-shrink: 0; }
.sidebar a { display: flex; align-items: center; gap: 15px; padding: 15px 30px; color: #6b6b6b; text-decoration: none; font-size: 14px; font-weight: 500; letter-spacing: 1px; transition: 0.3s; border-left: 3px solid transparent; }
.sidebar a:hover { background: #fdfbf7; color: #b8860b; }
.sidebar a.active { background: linear-gradient(135deg, #fef9f0, #fdf4e3); color: #b8860b; border-left-color: #b8860b; }
.sidebar a i { font-size: 18px; width: 20px; }
.admin-content { flex: 1; padding: 40px; }
.page-title { font-family: 'Playfair Display', serif; font-size: 36px; margin-bottom: 30px; }
.page-title span { color: #b8860b; font-style: italic; }
.form-card, .posts-card { background: white; padding: 30px; border-radius: 12px; border: 1px solid rgba(184,134,11,0.15); margin-bottom: 30px; }
.form-card h3, .posts-card h3 { font-family: 'Playfair Display', serif; font-size: 22px; margin-bottom: 20px; color: #2a2a2a; }
.form-group { margin-bottom: 15px; }
.form-group input, .form-group textarea { width: 100%; padding: 12px 20px; border: 1px solid rgba(184,134,11,0.3); border-radius: 8px; font-size: 14px; font-family: 'Inter', sans-serif; resize: vertical; }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: #b8860b; }
.form-group textarea { min-height: 120px; }
.btn-primary { display: inline-flex; align-items: center; gap: 10px; background: #b8860b; color: white; padding: 12px 25px; border-radius: 8px; text-decoration: none; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; font-weight: 500; border: none; cursor: pointer; transition: 0.3s; }
.btn-primary:hover { background: #d4a017; transform: translateY(-2px); box-shadow: 0 10px 25px rgba(184,134,11,0.3); }
.post-item { padding: 20px; border-bottom: 1px solid rgba(184,134,11,0.1); display: flex; justify-content: space-between; align-items: center; gap: 20px; }
.post-item:last-child { border-bottom: none; }
.post-item h4 { font-family: 'Playfair Display', serif; font-size: 18px; margin-bottom: 5px; }
.post-item small { color: #999; font-size: 12px; }
.post-item .view-btn { background: #b8860b; color: white; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-size: 13px; letter-spacing: 1px; }
@media (max-width: 768px) {
    .admin-header { padding: 0 20px; }
    .admin-user span { display: none; }
    .sidebar { width: 70px; }
    .sidebar a { padding: 15px; justify-content: center; }
    .sidebar a span { display: none; }
    .admin-content { padding: 20px; }
    .page-title { font-size: 24px; }
}
</style>
</head>
<body>

<div class="admin-header">
    <div class="admin-logo">ДАНИИЛ <span>· АДМИН</span></div>
    <div class="admin-user">
        <span><i class="fas fa-user"></i> Администратор</span>
        <a href="/logout" class="logout-btn"><i class="fas fa-sign-out-alt"></i> Выйти</a>
    </div>
</div>

<div class="admin-layout">
    <div class="sidebar">
        <a href="/admin"><i class="fas fa-chart-line"></i> <span>Дашборд</span></a>
        <a href="/admin/messages"><i class="fas fa-envelope"></i> <span>Заявки</span></a>
        <a href="/admin/blog" class="active"><i class="fas fa-blog"></i> <span>Блог</span></a>
        <a href="/" target="_blank"><i class="fas fa-external-link-alt"></i> <span>На сайт</span></a>
    </div>

    <div class="admin-content">
        <h1 class="page-title">📝 <span>Блог</span></h1>

        <div class="form-card">
            <h3>➕ Добавить статью</h3>
            <form method="POST" action="/admin/add_post">
                <div class="form-group">
                    <input type="text" name="title" placeholder="Заголовок статьи" required>
                </div>
                <div class="form-group">
                    <textarea name="content" placeholder="Текст статьи..." required></textarea>
                </div>
                <button type="submit" class="btn-primary"><i class="fas fa-plus"></i> Опубликовать</button>
            </form>
        </div>

        <div class="posts-card">
            <h3>📚 Все статьи ({{ posts|length }})</h3>
            {% for post in posts %}
            <div class="post-item">
                <div>
                    <h4>{{ post[1] }}</h4>
                    <small>{{ post[3] }}</small>
                </div>
                <a href="/post/{{ post[0] }}" target="_blank" class="view-btn"><i class="fas fa-eye"></i> Открыть</a>
            </div>
            {% endfor %}
            {% if posts|length == 0 %}
            <p style="color:#999;padding:20px 0">Пока нет статей. Добавь первую!</p>
            {% endif %}
        </div>
    </div>
</div>

</body>
</html>
'''


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
