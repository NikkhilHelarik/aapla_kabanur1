import os, sqlite3, functools
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash as gh, check_password_hash as ch

app = Flask(__name__)
import config
app.secret_key = config.SECRET_KEY
DB_PATH = config.DB_PATH

SECTIONS = {  # key: (title, icon)
 "village": ("Village Information", "fa-mountain-sun"), "panchayat": ("Gram Panchayat", "fa-landmark"),
 "schemes": ("Government Schemes", "fa-hand-holding-heart"), "news": ("News & Announcements", "fa-bullhorn"),
 "education": ("Education", "fa-graduation-cap"), "health": ("Healthcare", "fa-house-medical"),
 "agriculture": ("Agriculture", "fa-wheat-awn"), "jobs": ("Job Portal", "fa-briefcase")}
COMPLAINTS = ["Road Problems", "Water Supply", "Electricity", "Drainage", "Garbage Collection", "Street Lights"]
TAXES = ["House Tax", "Water Tax", "Shop Tax", "Cleaning Tax", "Other Panchayat Tax"]
CERTS = ["Birth Certificate", "Death Certificate", "Residence Certificate"]

def db():
    c = sqlite3.connect(DB_PATH, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

def q(sql, a=(), one=False, ret_id=False):
    sql = sql.replace("%s", "?").replace("NOW()", "CURRENT_TIMESTAMP")
    c = db()
    try:
        cur = c.execute(sql, a)
        c.commit()
        if ret_id: return cur.lastrowid
        if cur.description is None: return None
        if one:
            r = cur.fetchone()
            return dict(r) if r else None
        return [dict(r) for r in cur.fetchall()]
    finally:
        c.close()

def init_db():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    c = db()
    c.executescript(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql"), encoding="utf8").read())
    c.commit(); c.close()
    if not q("SELECT id FROM users WHERE username='admin'", one=True):
        q("INSERT INTO users(name,username,password,role) VALUES('Administrator','admin',%s,'admin')", (gh("admin@123"),))
    if not q("SELECT id FROM users WHERE username='ramesh'", one=True):
        uid = q("INSERT INTO users(name,username,password,phone,house_no) VALUES('Ramesh Patil','ramesh',%s,'9800000000','H-101')", (gh("Pass@123"),), ret_id=True)
        q("INSERT INTO taxes(user_id,type,amount,year) VALUES(%s,'House Tax',1200,'2026-27'),(%s,'Water Tax',450,'2026-27')", (uid, uid))
    if not q("SELECT id FROM content LIMIT 1", one=True):
        for s, t, b in [
            ("village", "About Kabanur", "Kabanur is a village in Maharashtra. Edit history, population, location and gallery from the admin panel."),
            ("panchayat", "Sarpanch", "Name and contact details. Office hours: Mon–Sat, 10:00 AM – 5:00 PM."),
            ("schemes", "PM Awas Yojana (Gramin)", "Eligibility, required documents and application steps can be added here."),
            ("news", "Gram Sabha Meeting", "The next Gram Sabha will be announced here."),
            ("education", "Zilla Parishad Primary School", "Primary, high school, college and scholarship information."),
            ("health", "Primary Health Centre", "Emergency: 108 | Ambulance: 102"),
            ("agriculture", "Crop Market Rates", "Daily mandi rates and weather updates."),
            ("jobs", "Skill Development Programs", "Government, private and local job openings.")]:
            q("INSERT INTO content(section,title,body) VALUES(%s,%s,%s)", (s, t, b))

def login_required(role=None):
    def deco(f):
        @functools.wraps(f)
        def w(*a, **k):
            if "uid" not in session:
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                abort(403)
            return f(*a, **k)
        return w
    return deco

@app.template_filter("dt")
def dt_filter(v, fmt="%d %b %Y"):
    if not v: return "—"
    try: return datetime.strptime(str(v)[:19], "%Y-%m-%d %H:%M:%S").strftime(fmt)
    except ValueError: return str(v)

@app.template_filter("inr")
def inr_filter(v):
    try:
        v = float(v)
        return f"{v:.0f}" if v == int(v) else f"{v:.2f}"
    except (TypeError, ValueError):
        return v

@app.context_processor
def inject():
    return dict(SECTIONS=SECTIONS, WX=dict(lat=config.WEATHER_LAT, lon=config.WEATHER_LON, place=config.WEATHER_PLACE))

@app.route("/")
def home():
    return render_template("home.html", news=q("SELECT * FROM content WHERE section='news' ORDER BY id DESC LIMIT 3"))

@app.route("/s/<key>")
def section(key):
    if key not in SECTIONS: abort(404)
    return render_template("section.html", key=key, items=q("SELECT * FROM content WHERE section=%s ORDER BY id DESC", (key,)))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = q("SELECT * FROM users WHERE username=%s", (request.form["username"].strip(),), one=True)
        if u and ch(u["password"], request.form["password"]):
            session.update(uid=u["id"], name=u["name"], role=u["role"])
            return redirect(url_for("admin" if u["role"] == "admin" else "dashboard"))
        flash("Wrong username or password.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        f = request.form
        if q("SELECT id FROM users WHERE username=%s", (f["username"],), one=True):
            flash("That username is taken.", "danger")
        else:
            q("INSERT INTO users(name,username,password,phone,house_no,address) VALUES(%s,%s,%s,%s,%s,%s)",
              (f["name"], f["username"], gh(f["password"]), f["phone"], f["house_no"], f["address"]))
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required()
def dashboard():
    if session["role"] == "admin": return redirect(url_for("admin"))
    u = session["uid"]
    return render_template("dashboard.html", me=q("SELECT * FROM users WHERE id=%s", (u,), one=True),
        taxes=q("SELECT * FROM taxes WHERE user_id=%s ORDER BY id DESC", (u,)),
        complaints=q("SELECT * FROM complaints WHERE user_id=%s ORDER BY id DESC", (u,)),
        certs=q("SELECT * FROM certificates WHERE user_id=%s ORDER BY id DESC", (u,)),
        CATS=COMPLAINTS, CERTS=CERTS)

@app.post("/complaint")
@login_required()
def complaint():
    q("INSERT INTO complaints(user_id,category,description) VALUES(%s,%s,%s)", (session["uid"], request.form["category"], request.form["description"]))
    flash("Complaint submitted.", "success")
    return redirect(url_for("dashboard"))

@app.post("/certificate")
@login_required()
def certificate():
    q("INSERT INTO certificates(user_id,type,details) VALUES(%s,%s,%s)", (session["uid"], request.form["type"], request.form["details"]))
    flash("Application submitted. Issuance needs Gram Panchayat approval.", "success")
    return redirect(url_for("dashboard"))

@app.post("/pay/<int:tid>")
@login_required()
def pay(tid):
    # Demo gateway: replace this block with Razorpay/PhonePe/UPI callback verification.
    t = q("SELECT * FROM taxes WHERE id=%s AND user_id=%s AND status='Pending'", (tid, session["uid"]), one=True)
    if t:
        q("UPDATE taxes SET status='Paid',mode='Online',paid_on=NOW(),receipt_no=%s WHERE id=%s", (f"AK{datetime.now():%Y%m%d%H%M%S}{tid}", tid))
        flash("Payment successful (demo gateway).", "success")
    return redirect(url_for("dashboard"))

@app.route("/receipt/<int:tid>")
@login_required()
def receipt(tid):
    t = q("SELECT t.*,u.name,u.house_no FROM taxes t JOIN users u ON u.id=t.user_id WHERE t.id=%s AND t.status='Paid'", (tid,), one=True)
    if not t or (session["role"] != "admin" and t["user_id"] != session["uid"]): abort(404)
    return render_template("receipt.html", t=t)

@app.route("/admin")
@login_required("admin")
def admin():
    n = lambda s: q(s, one=True)["n"]
    stats = dict(users=n("SELECT COUNT(*) n FROM users WHERE role='citizen'"), pending=n("SELECT COUNT(*) n FROM complaints WHERE status<>'Resolved'"),
                 collected=n("SELECT COALESCE(SUM(amount),0) n FROM taxes WHERE status='Paid'"), certs=n("SELECT COUNT(*) n FROM certificates WHERE status='Pending'"))
    return render_template("admin.html", stats=stats, users=q("SELECT * FROM users WHERE role='citizen'"),
        complaints=q("SELECT c.*,u.name FROM complaints c JOIN users u ON u.id=c.user_id ORDER BY c.id DESC"),
        taxes=q("SELECT t.*,u.name FROM taxes t JOIN users u ON u.id=t.user_id ORDER BY t.id DESC"),
        certs=q("SELECT c.*,u.name FROM certificates c JOIN users u ON u.id=c.user_id ORDER BY c.id DESC"),
        content=q("SELECT * FROM content ORDER BY section,id DESC"), TAXES=TAXES)

def back(): return redirect(request.referrer or url_for("admin"))

@app.post("/admin/content")
@login_required("admin")
def add_content():
    f = request.form
    q("INSERT INTO content(section,title,body) VALUES(%s,%s,%s)", (f["section"], f["title"], f["body"]))
    return back()

@app.post("/admin/content/<int:i>/edit")
@login_required("admin")
def edit_content(i):
    f = request.form
    q("UPDATE content SET section=%s,title=%s,body=%s WHERE id=%s", (f["section"], f["title"], f["body"], i))
    flash("Content updated.", "success")
    return back()

@app.post("/admin/content/<int:i>/delete")
@login_required("admin")
def del_content(i):
    q("DELETE FROM content WHERE id=%s", (i,)); return back()

@app.post("/admin/complaint/<int:i>")
@login_required("admin")
def set_complaint(i):
    q("UPDATE complaints SET status=%s WHERE id=%s", (request.form["status"], i)); return back()

@app.post("/admin/cert/<int:i>")
@login_required("admin")
def set_cert(i):
    q("UPDATE certificates SET status=%s WHERE id=%s", (request.form["status"], i)); return back()

@app.post("/admin/tax")
@login_required("admin")
def add_tax():
    f = request.form
    q("INSERT INTO taxes(user_id,type,amount,year) VALUES(%s,%s,%s,%s)", (f["user_id"], f["type"], f["amount"], f["year"])); return back()

@app.post("/admin/tax/<int:i>/cash")
@login_required("admin")
def cash(i):
    q("UPDATE taxes SET status='Paid',mode='Offline (Cash)',paid_on=NOW(),verified=1,receipt_no=%s WHERE id=%s AND status='Pending'", (f"AK{datetime.now():%Y%m%d%H%M%S}{i}", i)); return back()

@app.post("/admin/tax/<int:i>/verify")
@login_required("admin")
def verify(i):
    q("UPDATE taxes SET verified=1 WHERE id=%s", (i,)); return back()

init_db()   # creates tables + default users automatically (runs under gunicorn too)

if __name__ == "__main__":
    print("Database ready:", DB_PATH, "- open http://127.0.0.1:5000")
    app.run(debug=True, port=int(os.getenv("PORT", "5000")))
