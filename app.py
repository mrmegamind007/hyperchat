from flask import Flask, render_template_string, request, redirect, session, jsonify, send_from_directory
import sqlite3
import datetime
import hashlib
import os
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('.', 'sw.js')

@app.route('/icon-192.png')
def icon192():
    return send_from_directory('.', 'icon.jpeg')

@app.route('/icon-512.png')
def icon512():
    return send_from_directory('.', 'icon.jpeg')

@app.route('/icon.png')
def icon():
    return send_from_directory('.', 'icon.jpeg'
    
app.secret_key = "hyperchat_final_verified_2026"
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DB = "hyperchat.db"


def get_db(): return sqlite3.connect(DB, check_same_thread=False)


COURSES = ["Computer Science", "Software Engineering", "Data Science", "AI", "Cybersecurity", "Information Systems", "Mechanical Engineering", "Civil Engineering", "Electrical Engineering", "Chemical Engineering", "Mining Engineering", "Medicine", "Nursing", "Pharmacy", "Dentistry", "Physiotherapy", "Veterinary Science", "Law", "LLB", "Accounting", "Finance", "Economics", "Business Management", "Marketing", "Entrepreneurship", "Human Resources", "Psychology", "Social Work", "Sociology", "Education", "Foundation Phase",
           "Graphic Design", "Fine Arts", "Architecture", "Interior Design", "Journalism", "Media Studies", "Communication", "Film & TV", "Music", "Theology", "Political Science", "International Relations", "Agriculture", "Environmental Science", "Biochemistry", "Biotechnology", "Mathematics", "Statistics", "Physics", "Chemistry", "Quantity Surveying", "Construction Management", "Tourism", "Hospitality", "Fashion Design", "Public Health", "Occupational Therapy", "Optometry", "Dietetics", "Quantity Surveying", "Actuarial Science", "BCom"]

COUNTRIES = ["South Africa", "Zimbabwe", "Nigeria", "Kenya", "Ghana", "Botswana", "Namibia", "Lesotho", "Eswatini", "Zambia", "Malawi", "Tanzania",
             "Uganda", "Rwanda", "DR Congo", "Ethiopia", "Egypt", "Morocco", "USA", "UK", "Canada", "Australia", "India", "China", "Germany", "France"]

VERIFIED_DOMAINS = ["ufs.ac.za", "ac.za",
                    "edu", "cut.ac.za", "nwu.ac.za", "up.ac.za"]

conn = get_db()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, username TEXT UNIQUE, email TEXT UNIQUE, password TEXT, dob TEXT, country_birth TEXT, country_reside TEXT, university TEXT, courses TEXT, user_type TEXT, verified INTEGER DEFAULT 0, dark_mode INTEGER DEFAULT 0, bio TEXT DEFAULT '', profile_pic TEXT DEFAULT '')''')
c.execute('''CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, user_id INTEGER, content TEXT, image TEXT, category TEXT, visibility TEXT DEFAULT 'everyone', time TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS stories (id INTEGER PRIMARY KEY, user_id INTEGER, image TEXT, caption TEXT, time TEXT, expires TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS polls (id INTEGER PRIMARY KEY, user_id INTEGER, question TEXT, option1 TEXT, option2 TEXT, option3 TEXT, option4 TEXT, visibility TEXT DEFAULT 'everyone', time TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS poll_votes (id INTEGER PRIMARY KEY, poll_id INTEGER, user_id INTEGER, choice INTEGER, UNIQUE(poll_id, user_id))''')
c.execute('''CREATE TABLE IF NOT EXISTS groups (id INTEGER PRIMARY KEY, name TEXT, description TEXT, created_by INTEGER, image TEXT, university TEXT, is_uni INTEGER DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS group_members (group_id INTEGER, user_id INTEGER, PRIMARY KEY(group_id, user_id))''')
c.execute('''CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY, post_id INTEGER, user_id INTEGER, content TEXT, time TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS likes (id INTEGER PRIMARY KEY, post_id INTEGER, user_id INTEGER, UNIQUE(post_id, user_id))''')
c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, sender_id INTEGER, receiver_id INTEGER, content TEXT, image TEXT, time TEXT, read INTEGER DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY, user_id INTEGER, content TEXT, link TEXT, read INTEGER DEFAULT 0, time TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS marketplace (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, price REAL, description TEXT, category TEXT, image TEXT, time TEXT)''')
conn.commit()

BASE = '''<!doctype html><html><head><link rel="manifest" href="/manifest.json"><title>HyperChat</title><meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<style>
:root{--bg:#f8fafc;--card:white;--text:#0f172a;--accent:#115e59;--border:#e2e8f0;--blue:#1d9bf0}
body.dark{--bg:#020617;--card:#0f172a;--text:#f1f5f9;--accent:#14b8a6;--border:#1e293b}
body{font-family:'DM Sans',Arial;background:var(--bg);color:var(--text);margin:0;padding-bottom:80px}
nav{display:flex;justify-content:space-between;align-items:center;padding:12px 20px;background:var(--card);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100}
.nav-links{display:flex;gap:14px;align-items:center}
.logo{font-size:26px;font-weight:900;color:var(--accent)}
.logo.big{font-size:90px;line-height:0.5;vertical-align:middle}
.card{background:var(--card);padding:15px;margin:10px 0;border-radius:16px;border:1px solid var(--border)}
input,textarea,select,button{width:95%;padding:11px;margin:5px 0;border:1px solid var(--border);border-radius:10px;font-size:14px;background:var(--card);color:var(--text)}
button{background:var(--accent);color:white;border:none;cursor:pointer;font-weight:bold;border-radius:12px}
a.link{color:var(--accent);text-decoration:none;font-weight:bold}
.search-results{border:1px solid var(--border);border-radius:10px;max-height:160px;overflow-y:auto;background:var(--card);position:absolute;width:90%;z-index:20}
.search-item{padding:10px;cursor:pointer}.search-item:hover{background:var(--accent);color:white}
.container{max-width:780px;margin:auto;padding:12px}
.badge{padding:5px 10px;border-radius:20px;font-size:10px;color:white;font-weight:800}
.badge.everyone{background:var(--accent)}.badge.university{background:#0369a1}.badge.course{background:#6d28d9}.badge.verified{background:var(--blue)}
.profile-pic{width:38px;height:38px;border-radius:50%;object-fit:cover}
.composer{background:var(--card);border:1.5px solid var(--border);border-radius:24px;padding:20px}
.composer-top{display:flex;gap:14px;align-items:center}
.composer-avatar{width:52px;height:52px;border-radius:50%;border:2px solid var(--accent);object-fit:cover}
.composer-input{flex:1;background:var(--bg);border:1px solid var(--border);border-radius:24px;padding:16px 20px;font-size:15px;outline:none;resize:none}
.chips{display:flex;gap:8px;margin-top:14px;overflow-x:auto}
.chip{padding:7px 14px;border-radius:20px;border:1.5px solid var(--border);background:var(--bg);font-weight:700;font-size:12px;cursor:pointer;white-space:nowrap}
.chip.active{background:var(--accent);color:white;border-color:var(--accent)}
.visibility-row{display:flex;gap:8px;margin-top:12px}
.vis-btn{flex:1;padding:9px;border-radius:14px;border:1.5px solid var(--border);background:var(--bg);font-weight:700;font-size:11px;cursor:pointer;text-align:center}
.vis-btn.active{border-color:var(--accent);background:var(--accent);color:white}
.post-card{background:var(--card);border-radius:18px;padding:16px;margin:12px 0;border:1px solid var(--border)}
.stories-bar{display:flex;gap:14px;overflow-x:auto;padding:12px 4px;margin-bottom:14px;scrollbar-width:none}
.stories-bar::-webkit-scrollbar{display:none}
.story-item{text-align:center;min-width:68px;cursor:pointer}
.story-ring{width:64px;height:64px;border-radius:50%;padding:3px;background:linear-gradient(45deg, #115e59, #14b8a6, #f59e0b);display:flex;align-items:center;justify-content:center}
.story-ring img{width:58px;height:58px;border-radius:50%;border:3px solid var(--card);object-fit:cover}
.story-username{font-size:11px;margin-top:4px;max-width:68px;overflow:hidden}
.story-add{position:relative}.story-add-btn{position:absolute;bottom:2px;right:2px;background:var(--accent);color:white;border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center;font-size:12px;border:2px solid var(--card)}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);z-index:1000;align-items:center;justify-content:center}
.modal.active{display:flex}.modal img{max-width:90%;max-height:80%;border-radius:16px}
.poll-option{padding:10px 14px;border:1.5px solid var(--border);border-radius:12px;margin:6px 0;cursor:pointer;position:relative;overflow:hidden;display:flex;justify-content:space-between}
.poll-fill{position:absolute;top:0;left:0;height:100%;background:var(--accent);opacity:0.15;transition:0.5s}
.poll-option.voted{border-color:var(--accent);background:rgba(17,94,89,0.08)}
.verify-banner{background:linear-gradient(135deg, #115e59, #0e7490);color:white;padding:12px 16px;border-radius:14px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center}
</style></head><body class="{{'dark' if user and user[12] else ''}}">
<nav><div class="logo"><span class="big">H</span>yper<span class="big">C</span>hat</div>
{% if user %}<div class="nav-links">
<a href="/" class="link"><i class="fa fa-house"></i></a>
<a href="/groups" class="link"><i class="fa fa-users"></i></a>
<a href="/marketplace" class="link"><i class="fa fa-store"></i></a>
<a href="/messages" class="link"><i class="fa fa-message"></i></a>
<a href="/notifications" class="link"><i class="fa fa-bell"></i></a>
<a href="/verify" class="link">{% if user[11] %}<i class="fa fa-circle-check" style="color:var(--blue)"></i>{% else %}<i class="fa fa-triangle-exclamation" style="color:orange"></i>{% endif %}</a>
<a href="/toggle_dark" class="link"><i class="fa {{'fa-sun' if user[12] else 'fa-moon'}}"></i></a>
<a href="/profile/{{user[0]}}" class="link"><img src="{{user[14] or 'https://i.imgur.com/I80W1Qb.png'}}" class="profile-pic"></a>
<a href="/logout" class="link"><i class="fa fa-right-from-bracket"></i></a>
</div>{% else %}<div><a href="/login" class="link">Login</a></div>{% endif %}</nav>
<div class="container">{{content|safe}}</div>
<div id="storyModal" class="modal" onclick="this.classList.remove('active')"><div style="text-align:center"><img id="modalImg"><p id="modalUser" style="color:white"></p><p id="modalCap" style="color:white;opacity:0.8"></p></div></div>
<script>function openStory(img,u,c){document.getElementById('modalImg').src=img;document.getElementById('modalUser').innerText=u;document.getElementById('modalCap').innerText=c;document.getElementById('storyModal').classList.add('active');}</script>
<script>if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js');}</script></body></html>'''


def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()


def current_user():
    if "user_id" not in session:
        return None
    conn = get_db()
    c = conn.cursor()
    return c.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()


def now(): return datetime.datetime.now().strftime("%d/%m %H:%M")
def now_plus_24(): return (datetime.datetime.now() +
                           datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")


def is_verified_user(u): return u[11] == 1 if u else False


@app.route("/static/uploads/<f>")
def uploaded_file(f): return send_from_directory(
    app.config['UPLOAD_FOLDER'], f)


@app.route("/api/search_uni")
def search_uni():
    q = request.args.get("q", "")
    if len(q) < 2:
        return jsonify([])
    try:
        r = requests.get(f"http://universities.hipolabs.com/search?name={q}")
        return jsonify([u['name'] for u in r.json()[:10]])
    except:
        return jsonify([])


@app.route("/toggle_dark")
def toggle_dark():
    user = current_user()
    if user:
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE users SET dark_mode=? WHERE id=?",
                  (0 if user[12] else 1, user[0]))
        conn.commit()
    return redirect(request.referrer or "/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        conn = get_db()
        c = conn.cursor()
        email = request.form["email"].lower()
        is_ver = 1 if any(d in email for d in VERIFIED_DOMAINS) else 0
        try:
            c.execute("INSERT INTO users (name,username,email,password,dob,country_birth,country_reside,university,courses,user_type,verified) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                      (request.form["name"], request.form["username"], email, hash_pw(request.form["password"]), request.form["dob"], request.form["country_birth"], request.form["country_reside"], request.form["university"], request.form["courses"], request.form["user_type"], is_ver))
            conn.commit()
            nid = c.lastrowid
            uni = request.form["university"].strip()
            ex = c.execute(
                "SELECT id FROM groups WHERE name=? AND is_uni=1", (uni,)).fetchone()
            if not ex:
                c.execute("INSERT INTO groups (name, description, created_by, university, is_uni) VALUES (?,?,?,?,1)",
                          (uni, f"Official {uni}", nid, uni))
                conn.commit()
                gid = c.lastrowid
            else:
                gid = ex[0]
            try:
                c.execute(
                    "INSERT INTO group_members (group_id, user_id) VALUES (?,?)", (gid, nid))
                conn.commit()
            except:
                pass
            return redirect("/login")
        except Exception as e:
            return f"<h2>Error: {e}</h2><a href='/register'>Back</a>"
    course_json = str(COURSES).replace("'", '"')
    country_opts = "".join([f'<option>{c}</option>' for c in COUNTRIES])
    content = f'''<div class="card"><h2>Create Account</h2><form method="POST">
    <input name="name" placeholder="Full Name" required><input name="username" placeholder="@username (will show)" required><input name="email" type="email" placeholder="Student Email - use @ufs.ac.za to get blue tick" required style="text-transform:none"><input name="password" type="password" placeholder="Password" required><input name="dob" type="date" required>
    <select name="country_birth" required><option value="">Country of Birth</option>{country_opts}</select><select name="country_reside" required><option value="">Country of Residence</option>{country_opts}</select>
    <input type="text" id="uniInput" placeholder="Search University..." required oninput="document.getElementById('uniHidden').value=this.value"><input name="university" id="uniHidden" type="hidden"><div id="uniResults" class="search-results" style="display:none"></div>
    <input type="text" id="courseInput" placeholder="Search Course..." required oninput="document.getElementById('courseHidden').value=this.value"><input name="courses" id="courseHidden" type="hidden"><div id="courseResults" class="search-results" style="display:none"></div>
    <select name="user_type"><option>Student</option><option>Business</option></select><button>Register</button></form></div>
    <script>const courses={course_json};function setupSearch(i,r,h,a){{const input=document.getElementById(i);const res=document.getElementById(r);const hid=document.getElementById(h);input.onkeyup=async function(){{if(input.value.length<2){{res.style.display="none";return;}}let d;if(a){{let x=await fetch(a+input.value);d=await x.json();}}else{{d=courses.filter(c=>c.toLowerCase().includes(input.value.toLowerCase()));}}res.innerHTML=d.map(x=>`<div class="search-item" onclick="selectItem('${{x}}','${{i}}','${{r}}','${{h}}')">${{x}}</div>`).join('');res.style.display=d.length?"block":"none";}}}}function selectItem(v,i,r,h){{document.getElementById(i).value=v;document.getElementById(h).value=v;document.getElementById(r).style.display="none";}}setupSearch("uniInput","uniResults","uniHidden","/api/search_uni?q=");setupSearch("courseInput","courseResults","courseHidden",null);</script>'''
    return render_template_string(BASE, content=content, user=None)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_db()
        c = conn.cursor()
        u = c.execute("SELECT * FROM users WHERE email=? AND password=?",
                      (request.form["email"].lower(), hash_pw(request.form["password"]))).fetchone()
        if u:
            session["user_id"] = u[0]
            return redirect("/")
        return "Invalid <a href='/login'>Try again</a>"
    content = '''<div class="card"><h2>Login</h2><form method="POST"><input name="email" type="email" placeholder="Email" style="text-transform:none" required><input name="password" type="password" placeholder="Password" required><button>Login</button></form><p><a href="/register" class="link">No account? Register</a></p></div>'''
    return render_template_string(BASE, content=content, user=None)


@app.route("/logout")
def logout(): session.clear(); return redirect("/login")


@app.route("/verify", methods=["GET", "POST"])
def verify():
    user = current_user()
    if not user:
        return redirect("/login")
    if request.method == "POST":
        sno = request.form.get("student_no", "")
        if len(sno) >= 8:
            conn = get_db()
            c = conn.cursor()
            c.execute("UPDATE users SET verified=1 WHERE id=?", (user[0],))
            conn.commit()
            return redirect("/")
    ver = user[11]
    content = f'''
    <div class="card" style="text-align:center">
        <h2><i class="fa fa-circle-check" style="color:var(--blue)"></i> Student Verification</h2>
        {'<p style="color:var(--blue);font-weight:bold">✅ You are Verified! You have blue tick</p>' if ver else '<p style="color:orange">⚠️ Not verified yet - verify to get blue tick</p>'}
        {'' if ver else '''
        <p style="font-size:13px">Enter your UFS student number. If you used @ufs.ac.za email you are auto-verified.</p>
        <form method="POST" enctype="multipart/form-data">
            <input name="student_no" placeholder="e.g. 2024123456" required pattern="[0-9]{8,10}">
            <p style="font-size:11px;opacity:0.7">In production, we would verify with UFS system. For demo, any 8+ digits verifies you.</p>
            <button>Verify Me <i class="fa fa-circle-check"></i></button>
        </form>
        '''}
        <br><a href="/" class="link">← Back to feed</a>
    </div>
    '''
    return render_template_string(BASE, content=content, user=user)


@app.route("/add_story", methods=["POST"])
def add_story():
    user = current_user()
    if not is_verified_user(user):
        return redirect("/verify")
    if 'image' in request.files and request.files['image'].filename:
        filename = secure_filename(request.files['image'].filename)
        request.files['image'].save(os.path.join(
            app.config['UPLOAD_FOLDER'], filename))
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO stories (user_id, image, caption, time, expires) VALUES (?,?,?,?,?)",
                  (user[0], filename, request.form.get("caption", ""), now(), now_plus_24()))
        conn.commit()
    return redirect("/")


@app.route("/create_poll", methods=["POST"])
def create_poll():
    user = current_user()
    if not is_verified_user(user):
        return redirect("/verify")
    q = request.form["question"]
    o1 = request.form["opt1"]
    o2 = request.form["opt2"]
    o3 = request.form.get("opt3", "")
    o4 = request.form.get("opt4", "")
    vis = request.form.get("visibility", "everyone")
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO polls (user_id, question, option1, option2, option3, option4, visibility, time) VALUES (?,?,?,?,?,?,?,?)",
              (user[0], q, o1, o2, o3, o4, vis, now()))
    conn.commit()
    return redirect("/")


@app.route("/vote_poll/<int:poll_id>/<int:choice>")
def vote_poll(poll_id, choice):
    user = current_user()
    if not user:
        return redirect("/login")
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO poll_votes (poll_id, user_id, choice) VALUES (?,?,?)",
                  (poll_id, user[0], choice))
        conn.commit()
    except:
        c.execute("UPDATE poll_votes SET choice=? WHERE poll_id=? AND user_id=?",
                  (choice, poll_id, user[0]))
        conn.commit()
    return redirect("/")


@app.route("/", methods=["GET", "POST"])
def home():
    user = current_user()
    if not user:
        return redirect("/login")
    conn = get_db()
    c = conn.cursor()
    if request.method == "POST":
        if not is_verified_user(user):
            return redirect("/verify")
        image = None
        if 'image' in request.files and request.files['image'].filename:
            filename = secure_filename(request.files['image'].filename)
            request.files['image'].save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename))
            image = filename
        c.execute("INSERT INTO posts (user_id, content, image, category, visibility, time) VALUES (?,?,?,?,?,?)",
                  (user[0], request.form["content"], image, request.form["category"], request.form["visibility"], now()))
        conn.commit()
        return redirect("/")
    c.execute("DELETE FROM stories WHERE expires < datetime('now','localtime')")
    conn.commit()
    my_uni = user[8]
    my_course = user[9]

    verify_banner = "" if is_verified_user(
        user) else f'''<div class="verify-banner"><div><b><i class="fa fa-triangle-exclamation"></i> Verify your student account</b><br><small>Get blue tick to post stories & polls</small></div><a href="/verify"><button style="width:auto;background:white;color:#115e59;padding:8px 16px;border-radius:20px">Verify</button></a></div>'''

    stories = c.execute(
        '''SELECT s.*, u.username, u.profile_pic, u.verified FROM stories s JOIN users u ON s.user_id=u.id WHERE u.university=? ORDER BY s.id DESC''', (my_uni,)).fetchall()
    stories_html = f'''<div class="story-item" onclick="document.getElementById('storyInput').click()"><div class="story-add"><div class="story-ring"><img src="{user[14] or 'https://i.imgur.com/I80W1Qb.png'}"></div><div class="story-add-btn">+</div></div><div class="story-username">Add Story</div></div>'''
    for s in stories:
        tick = '<i class="fa fa-circle-check" style="color:var(--blue);font-size:10px"></i>' if s[
            8] else ''
        stories_html += f'''<div class="story-item" onclick="openStory('/static/uploads/{s[2]}','@{s[7]} {tick}','{s[3] or ''}')"><div class="story-ring"><img src="{s[8-1] or 'https://i.imgur.com/I80W1Qb.png'}"></div><div class="story-username">@{s[7]}</div></div>'''

    all_posts = c.execute(
        '''SELECT p.*, u.username, u.profile_pic, u.university, u.courses, u.verified FROM posts p JOIN users u ON p.user_id=u.id ORDER BY p.id DESC''').fetchall()
    filtered_posts = [p for p in all_posts if p[1] == user[0] or (p[5] or 'everyone') == 'everyone' or (
        (p[5] == 'university' and p[9] == my_uni) or (p[5] == 'course' and p[10] == my_course))]

    all_polls = c.execute(
        '''SELECT p.*, u.username, u.profile_pic, u.university, u.courses, u.verified FROM polls p JOIN users u ON p.user_id=u.id ORDER BY p.id DESC''').fetchall()
    filtered_polls = [p for p in all_polls if p[1] == user[0] or (p[7] or 'everyone') == 'everyone' or (
        (p[7] == 'university' and p[10] == my_uni) or (p[7] == 'course' and p[11] == my_course))]

    feed_items = []
    for p in filtered_posts:
        feed_items.append(('post', p[0], p))
    for pl in filtered_polls:
        feed_items.append(('poll', pl[0], pl))
    feed_items.sort(key=lambda x: x[1], reverse=True)

    feed_html = ""
    for typ, _, item in feed_items:
        if typ == 'post':
            p = item
            likes = c.execute(
                "SELECT COUNT(*) FROM likes WHERE post_id=?", (p[0],)).fetchone()[0]
            liked = c.execute(
                "SELECT 1 FROM likes WHERE post_id=? AND user_id=?", (p[0], user[0])).fetchone()
            comments = c.execute(
                '''SELECT c.*, u.username FROM comments c JOIN users u ON c.user_id=u.id WHERE post_id=?''', (p[0],)).fetchall()
            comment_html = "".join(
                [f'<div style="margin-left:20px;font-size:13px;margin-top:6px"><b>@{com[4]}</b>: {com[3]}</div>' for com in comments])
            heart = "fa-solid" if liked else "fa-regular"
            img_tag = f'<img src="/static/uploads/{p[3]}" style="width:100%;border-radius:16px;margin-top:12px">' if p[3] else ""
            tick = '<i class="fa fa-circle-check" style="color:#1d9bf0"></i>' if p[12] else ''
            feed_html += f'''<div class="post-card"><div style="display:flex;align-items:center;gap:10px"><img src="{p[8] or 'https://i.imgur.com/I80W1Qb.png'}" class="profile-pic"><div><div style="font-weight:700">@{p[7]} {tick}</div><div style="font-size:11px;color:#64748b">{p[10]}</div></div><span style="margin-left:auto;font-size:11px">{p[6]}</span></div><span style="background:var(--bg);padding:4px 10px;border-radius:12px;font-size:11px;font-weight:bold;margin-top:8px;display:inline-block">#{p[4]}</span><p style="font-size:15px;margin:10px 0">{p[2]}</p>{img_tag}<div style="margin-top:12px;display:flex;gap:10px"><a href="/like/{p[0]}" style="background:var(--bg);padding:6px 14px;border-radius:20px;text-decoration:none;color:var(--text);font-size:13px"><i class="{heart} fa-heart" style="color:var(--accent)"></i> {likes}</a> <span style="background:var(--bg);padding:6px 14px;border-radius:20px;font-size:13px"><i class="fa fa-comment"></i> {len(comments)}</span></div>{comment_html}<form method="POST" action="/comment/{p[0]}" style="margin-top:10px;display:flex;gap:8px"><input name="content" placeholder="Reply..." style="border-radius:20px" required><button style="border-radius:20px;width:80px">Reply</button></form></div>'''
        else:
            pl = item
            total = c.execute(
                "SELECT COUNT(*) FROM poll_votes WHERE poll_id=?", (pl[0],)).fetchone()[0] or 1
            my_vote = c.execute(
                "SELECT choice FROM poll_votes WHERE poll_id=? AND user_id=?", (pl[0], user[0])).fetchone()
            my_choice = my_vote[0] if my_vote else -1
            opts = [pl[2], pl[3], pl[4], pl[5]]
            opts = [o for o in opts if o]
            poll_html = ""
            for idx, opt in enumerate(opts, start=1):
                cnt = c.execute(
                    "SELECT COUNT(*) FROM poll_votes WHERE poll_id=? AND choice=?", (pl[0], idx)).fetchone()[0]
                pct = int((cnt/total*100) if total > 0 else 0)
                voted_class = "voted" if my_choice == idx else ""
                poll_html += f'''<a href="/vote_poll/{pl[0]}/{idx}" style="text-decoration:none;color:var(--text)"><div class="poll-option {voted_class}"><div class="poll-fill" style="width:{pct}%"></div><span style="position:relative">{opt}</span><span style="position:relative;font-weight:bold">{pct}%</span></div></a>'''
            tick = '<i class="fa fa-circle-check" style="color:#1d9bf0"></i>' if pl[12] else ''
            feed_html += f'''<div class="post-card" style="border-left:3px solid #6d28d9"><div style="display:flex;align-items:center;gap:10px"><img src="{pl[9] or 'https://i.imgur.com/I80W1Qb.png'}" class="profile-pic"><div><div style="font-weight:700">@{pl[8]} {tick} • Poll</div></div><span style="margin-left:auto;font-size:11px">{pl[12]}</span></div><p style="font-weight:700;margin:12px 0;font-size:16px">{pl[2]}</p>{poll_html}<div style="font-size:11px;color:#64748b;margin-top:8px">{total} votes</div></div>'''

    safe_course = my_course[:18]
    content = f'''
    {verify_banner}
    <div class="stories-bar">{stories_html}</div>
    <form id="storyForm" action="/add_story" method="POST" enctype="multipart/form-data" style="display:none"><input type="file" id="storyInput" name="image" accept="image/*" onchange="if(confirm('Post story for 24h?')){{this.form.submit()}}"></form>
    <div style="display:flex;gap:8px;margin-bottom:12px">
        <button onclick="document.getElementById('postComposer').style.display='block';document.getElementById('pollComposer').style.display='none'" style="flex:1">📝 Post</button>
        <button onclick="document.getElementById('pollComposer').style.display='block';document.getElementById('postComposer').style.display='none'" style="flex:1;background:#6d28d9">📊 Poll</button>
    </div>
    <div id="pollComposer" class="composer" style="display:none;border-color:#6d28d9">
        <h3>📊 Create Poll</h3>
        <form method="POST" action="/create_poll">
            <textarea name="question" placeholder="Ask a question..." required></textarea>
            <input name="opt1" placeholder="Option 1" required><input name="opt2" placeholder="Option 2" required><input name="opt3" placeholder="Option 3 (optional)"><input name="opt4" placeholder="Option 4 (optional)">
            <div class="visibility-row"><div class="vis-btn active" onclick="selectVisPoll(this,'everyone')">🌍 Everyone</div><div class="vis-btn" onclick="selectVisPoll(this,'university')">🎓 My Uni</div><div class="vis-btn" onclick="selectVisPoll(this,'course')">📚 Course</div></div>
            <input type="hidden" name="visibility" id="visPollHidden" value="everyone">
            <button style="background:#6d28d9;margin-top:10px">Create Poll</button>
        </form>
    </div>
    <div id="postComposer" class="composer">
        <form method="POST" enctype="multipart/form-data">
            <div class="composer-top"><img src="{user[14] or 'https://i.imgur.com/I80W1Qb.png'}" class="composer-avatar"><textarea name="content" class="composer-input" placeholder="What's happening, @{user[2]}?" rows="1" required maxlength="500" oninput="document.getElementById('charCount').innerText=this.value.length+'/500'"></textarea></div>
            <div class="chips"><div class="chip active" onclick="selectCat(this)">#General</div><div class="chip" onclick="selectCat(this)">#CampusLife</div><div class="chip" onclick="selectCat(this)">#Memes</div><div class="chip" onclick="selectCat(this)">#Crush</div><div class="chip" onclick="selectCat(this)">#Events</div><div class="chip" onclick="selectCat(this)">#{safe_course}</div></div>
            <input type="hidden" name="category" id="catHidden" value="General">
            <div class="visibility-row"><div class="vis-btn active" onclick="selectVis(this,'everyone')">🌍 Everyone</div><div class="vis-btn" onclick="selectVis(this,'university')">🎓 My Uni</div><div class="vis-btn" onclick="selectVis(this,'course')">📚 Course</div></div>
            <input type="hidden" name="visibility" id="visHidden" value="everyone">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:16px;padding-top:12px;border-top:1px solid var(--border)"><div><label for="imgUpload" style="cursor:pointer;color:var(--accent)"><i class="fa fa-image" style="font-size:20px"></i></label><input type="file" id="imgUpload" name="image" accept="image/*" style="display:none"><span id="fileName" style="font-size:11px;margin-left:8px"></span></div><div style="display:flex;gap:10px;align-items:center"><span id="charCount" style="font-size:11px;color:#64748b">0/500</span><button style="border-radius:20px;padding:9px 24px;width:auto;margin:0">Post</button></div></div>
        </form>
    </div>
    <script>
    function selectCat(el){{document.querySelectorAll('#postComposer.chip').forEach(c=>c.classList.remove('active'));el.classList.add('active');document.getElementById('catHidden').value=el.innerText.replace('#','');}}
    function selectVis(el,val){{el.parentElement.querySelectorAll('.vis-btn').forEach(b=>b.classList.remove('active'));el.classList.add('active');document.getElementById('visHidden').value=val;}}
    function selectVisPoll(el,val){{el.parentElement.querySelectorAll('.vis-btn').forEach(b=>b.classList.remove('active'));el.classList.add('active');document.getElementById('visPollHidden').value=val;}}
    document.getElementById('imgUpload').onchange=function(){{document.getElementById('fileName').innerText=this.files[0].name;}}
    </script>
    {feed_html}
    '''
    return render_template_string(BASE, content=content, user=user)


@app.route("/like/<int:post_id>")
def like(post_id):
    user = current_user()
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO likes (post_id, user_id) VALUES (?,?)",
                  (post_id, user[0]))
        conn.commit()
    except:
        c.execute("DELETE FROM likes WHERE post_id=? AND user_id=?",
                  (post_id, user[0]))
        conn.commit()
    return redirect("/")


@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
    user = current_user()
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO comments (post_id, user_id, content, time) VALUES (?,?,?,?)",
              (post_id, user[0], request.form["content"], now()))
    conn.commit()
    return redirect("/")


@app.route("/groups", methods=["GET", "POST"])
def groups():
    user = current_user()
    conn = get_db()
    c = conn.cursor()
    my_uni = user[8]
    if request.method == "POST":
        c.execute("INSERT INTO groups (name, description, created_by, university, is_uni) VALUES (?,?,?,?,0)",
                  (request.form["name"], request.form["desc"], user[0], my_uni))
        conn.commit()
        gid = c.lastrowid
        c.execute(
            "INSERT INTO group_members (group_id, user_id) VALUES (?,?)", (gid, user[0]))
        conn.commit()
        return redirect(f"/group/{gid}")
    my_groups = c.execute(
        '''SELECT g.* FROM groups g JOIN group_members gm ON g.id=gm.group_id WHERE gm.user_id=?''', (user[0],)).fetchall()
    uni_groups = c.execute(
        "SELECT * FROM groups WHERE university=? AND is_uni=1", (my_uni,)).fetchall()

    def group_card(g, joined=False):
        badge = '<span class="badge university">UNI</span>' if g[5] else '<span class="badge course">GROUP</span>'
        btn = f'<a href="/group/{g[0]}"><button style="width:auto;border-radius:20px;padding:6px 16px">View</button></a>' if joined else f'<a href="/join_group/{g[0]}"><button style="width:auto;border-radius:20px;padding:6px 16px">Join</button></a>'
        return f'<div class="card">{badge} <b>{g[1]}</b><br>{btn}</div>'
    content = f'''<h2>My Groups</h2>{"".join([group_card(g, True) for g in my_groups])}<h2>Official</h2>{"".join([group_card(g, any(g[0] == mg[0] for mg in my_groups)) for g in uni_groups])}<div class="card"><h3>Create Group</h3><form method="POST"><input name="name" placeholder="Group Name" required><textarea name="desc"></textarea><button>Create</button></form></div>'''
    return render_template_string(BASE, content=content, user=user)


@app.route("/join_group/<int:group_id>")
def join_group(group_id):
    user = current_user()
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO group_members (group_id, user_id) VALUES (?,?)", (group_id, user[0]))
        conn.commit()
    except:
        pass
    return redirect(f"/group/{group_id}")


@app.route("/group/<int:group_id>")
def group_detail(group_id):
    user = current_user()
    conn = get_db()
    c = conn.cursor()
    g = c.execute("SELECT * FROM groups WHERE id=?", (group_id,)).fetchone()
    members = c.execute(
        '''SELECT u.id, u.username, u.verified FROM users u JOIN group_members gm ON u.id=gm.user_id WHERE gm.group_id=?''', (group_id,)).fetchall()
    members_html = "".join(
        [f'<div class="card">@{m[1]} {"<i class=\'fa fa-circle-check\' style=\'color:#1d9bf0\'></i>" if m[2] else ""}</div>' for m in members])
    content = f'<div class="card"><h2>{g[1]}</h2><p>{g[2]}</p><a href="/groups">← Back</a> | <a href="/leave_group/{group_id}" style="color:red">Leave</a></div>{members_html}'
    return render_template_string(BASE, content=content, user=user)


@app.route("/leave_group/<int:group_id>")
def leave_group(group_id):
    user = current_user()
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM group_members WHERE group_id=? AND user_id=?",
              (group_id, user[0]))
    conn.commit()
    return redirect("/groups")


@app.route("/messages")
def messages():
    user = current_user()
    conn = get_db()
    c = conn.cursor()
    users = c.execute(
        "SELECT id, username, verified FROM users WHERE id!=? AND university=?", (user[0], user[8])).fetchall()
    users_html = "".join(
        [f'<a href="/chat/{u[0]}" style="text-decoration:none"><div class="card">@{u[1]} {"<i class=\'fa fa-circle-check\' style=\'color:#1d9bf0\'></i>" if u[2] else ""}</div></a>' for u in users])
    content = f'<h2>Messages</h2>{users_html}'
    return render_template_string(BASE, content=content, user=user)


@app.route("/chat/<int:receiver_id>", methods=["GET", "POST"])
def chat(receiver_id):
    user = current_user()
    conn = get_db()
    c = conn.cursor()
    receiver = c.execute("SELECT * FROM users WHERE id=?",
                         (receiver_id,)).fetchone()
    if request.method == "POST":
        c.execute("INSERT INTO messages (sender_id, receiver_id, content, time) VALUES (?,?,?,?)",
                  (user[0], receiver_id, request.form["content"], now()))
        conn.commit()
        return redirect(f"/chat/{receiver_id}")
    msgs = c.execute("SELECT * FROM messages WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?) ORDER BY id",
                     (user[0], receiver_id, receiver_id, user[0])).fetchall()
    msgs_html = "".join(
        [f'<div style="padding:8px 14px;border-radius:18px;margin:6px 0;max-width:70%;{"background:var(--accent);color:white;margin-left:auto" if m[1] == user[0] else "background:var(--border)"}">{m[3]}</div>' for m in msgs])
    tick = '<i class="fa fa-circle-check" style="color:#1d9bf0"></i>' if receiver[11] else ''
    content = f'''<h2>Chat with @{receiver[2]} {tick}</h2><div style="height:400px;overflow-y:auto;border:1px solid var(--border);padding:12px;border-radius:16px">{msgs_html}</div><form method="POST" style="display:flex;gap:8px;margin-top:10px"><input name="content" placeholder="Message..." required style="border-radius:24px"><button style="width:80px;border-radius:24px">Send</button></form>'''
    return render_template_string(BASE, content=content, user=user)


@app.route("/notifications")
def notifications():
    user = current_user()
    conn = get_db()
    c = conn.cursor()
    notifs = c.execute(
        "SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC", (user[0],)).fetchall()
    notifs_html = "".join([f'<div class="card">{n[2]}</div>' for n in notifs])
    content = f'<h2>Notifications</h2>{notifs_html or "<p>No notifications</p>"}'
    return render_template_string(BASE, content=content, user=user)


@app.route("/marketplace", methods=["GET", "POST"])
def marketplace():
    user = current_user()
    conn = get_db()
    c = conn.cursor()
    if request.method == "POST":
        filename = None
        if 'image' in request.files and request.files['image'].filename:
            filename = secure_filename(request.files['image'].filename)
            request.files['image'].save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename))
        c.execute("INSERT INTO marketplace (user_id, title, price, description, category, image, time) VALUES (?,?,?,?,?,?,?)",
                  (user[0], request.form["title"], request.form["price"], request.form["desc"], request.form["cat"], filename, now()))
        conn.commit()
        return redirect("/marketplace")
    items = c.execute(
        '''SELECT m.*, u.username, u.verified FROM marketplace m JOIN users u ON m.user_id=u.id WHERE u.university=? ORDER BY m.id DESC''', (user[8],)).fetchall()
    items_html = "".join(
        [f'<div class="card"><b>{i[2]}</b> - R{i[3]}<br>{i[4]}<br><small>by @{i[8]} {"<i class=\'fa fa-circle-check\' style=\'color:#1d9bf0\'></i>" if i[9] else ""}</small></div>' for i in items])
    content = f'''<h2>Marketplace</h2><div class="card"><form method="POST" enctype="multipart/form-data"><input name="title" placeholder="Title" required><input name="price" type="number" step="0.01" placeholder="Price" required><textarea name="desc"></textarea><input name="cat" placeholder="Category"><input type="file" name="image" accept="image/*"><button>List</button></form></div>{items_html}'''
    return render_template_string(BASE, content=content, user=user)


@app.route("/profile/<int:user_id>")
def profile(user_id):
    user = current_user()
    conn = get_db()
    c = conn.cursor()
    prof = c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    posts = c.execute(
        "SELECT * FROM posts WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    posts_html = "".join(
        [f'<div class="card"><p>{p[2]}</p></div>' for p in posts])
    tick = '<i class="fa fa-circle-check" style="color:#1d9bf0"></i>' if prof[11] else ''
    content = f'''<div class="card" style="text-align:center"><img src="{prof[14] or 'https://i.imgur.com/I80W1Qb.png'}" style="width:90px;height:90px;border-radius:50%;border:3px solid var(--accent)"><h2>@{prof[2]} {tick}</h2><p>{prof[1]}</p><p>{'<span class="badge verified">Verified Student</span>' if prof[11] else '<span class="badge" style="background:orange">Unverified</span>'}</p><p>{prof[8]} • {prof[9]}</p></div>{posts_html}'''
    return render_template_string(BASE, content=content, user=user)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
