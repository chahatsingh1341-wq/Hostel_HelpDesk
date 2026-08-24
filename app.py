from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from module import (
    init_db,
    insert_credential,
    verify_credential,
    insert_complaint,
    get_all_complaints,
    get_user_complaints,
    insert_feedback,
    get_all_feedback,
    update_complaint_status,
    delete_old_resolved_complaints,
    get_user_by_email
)

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

@app.route('/')
def home():
    if session.get("role") == "student":
        return redirect(url_for("student_dashboard"))
    if session.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("login"))

@app.route('/create-demo-users')
def create_demo_users():
    insert_credential("student@gmail.com", "1234", "student")
    insert_credential("admin@gmail.com", "admin123", "admin")
    return "Demo users created"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        user = verify_credential(email, password, user_type)
        if user:
            session["email"] = email
            session["role"] = user_type
            return redirect(url_for("student_dashboard" if user_type == "student" else "admin_dashboard"))
        flash("Invalid login", "error")
    return render_template('login.html')

@app.route('/student-register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if get_user_by_email(email):
            flash("Email already exists", "error")
        else:
            insert_credential(email, password, "student")
            flash("Registration successful", "success")
            return redirect(url_for("login"))
    return render_template('student_register.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = verify_credential(email, password, "admin")
        if user:
            session["email"] = email
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin login", "error")
    return render_template('admin_login.html')

@app.route('/student-dashboard')
def student_dashboard():
    if session.get("role") != "student":
        return redirect(url_for("login"))
    blocks = ["Block A", "Block B", "Block C", "Block D"]
    complaints = get_user_complaints(session.get("email"))
    return render_template('student_dashboard.html', blocks=blocks, email=session.get("email"), complaints=complaints)

@app.route('/block/<block_name>')
def block_page(block_name):
    if session.get("role") != "student":
        return redirect(url_for("login"))
    floors = ["Ground Floor", "1st Floor", "2nd Floor", "3rd Floor"]
    return render_template('block_page.html', block_name=block_name, floors=floors)

@app.route('/block/<block_name>/floor/<floor>')
def floor_page(block_name, floor):
    if session.get("role") != "student":
        return redirect(url_for("login"))
    return render_template('floor_page.html', block_name=block_name, floor=floor)

@app.route('/block/<block_name>/floor/<floor>/corridor/<corridor>')
def corridor_page(block_name, floor, corridor):
    if session.get("role") != "student":
        return redirect(url_for("login"))
    return render_template('corridor_page.html', block_name=block_name, floor=floor, corridor=corridor)

@app.route('/submit-issue', methods=['GET', 'POST'])
def submit_issue():
    if session.get("role") != "student":
        return redirect(url_for("login"))
    block = request.args.get('block')
    floor = request.args.get('floor')
    corridor = request.args.get('corridor')
    issue_type = request.args.get('issue_type')
    
    if request.method == 'POST':
        block = request.form.get('block')
        floor = request.form.get('floor')
        corridor = request.form.get('corridor')
        room = request.form.get('room')
        issue_type = request.form.get('issue_type')
        issue_category = request.form.get('issue_category')
        insert_complaint(
            session.get("email"), "student", block, floor, corridor, room,
            issue_type, issue_category, datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        flash("Issue submitted successfully", "success")
        return redirect(url_for("student_dashboard"))
    
    return render_template('issue_form.html', block=block, floor=floor, corridor=corridor, issue_type=issue_type)

@app.route('/submit-feedback', methods=['GET', 'POST'])
def submit_feedback():
    if session.get("role") != "student":
        return redirect(url_for("login"))
    if request.method == 'POST':
        rating = request.form.get('rating')
        message = request.form.get('message')
        insert_feedback(session.get("email"), "student", rating, message, datetime.now().strftime("%Y-%m-%d %H:%M"))
        flash("Feedback submitted successfully", "success")
        return redirect(url_for("student_dashboard"))
    return render_template('feedback_form.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))
    complaints = get_all_complaints()
    feedbacks = get_all_feedback()
    return render_template('admin_dashboard.html', complaints=complaints, feedbacks=feedbacks)

@app.route('/admin-update/<int:cid>', methods=['POST'])
def admin_update(cid):
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))
    status = request.form.get('status')
    update_complaint_status(cid, status)
    flash("Status updated", "success")
    return redirect(url_for("admin_dashboard"))

@app.route('/cleanup-old-resolved')
def cleanup_old_resolved():
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))
    deleted = delete_old_resolved_complaints()
    flash(f"Deleted {deleted} old resolved complaints", "success")
    return redirect(url_for("admin_dashboard"))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)