from bcrypt import checkpw, gensalt, hashpw
from flask import Flask, abort, render_template, redirect, request, session
from traceback import print_exc
from classes import User

member_ids = []

try:
    for id in User.cursor.execute('SELECT username FROM users;'):
        member_ids.append(id[0])

    for id in member_ids:
        User(id)

    app = Flask(__name__)

    app.secret_key = b'016480fad86b560ddda3776246a9d959c718dab93e2632b8c93e29142ad46a73'

    @app.route("/")
    def home():
        if session.get("id"):
            user = User.get_user(session['id'])
            try:
                return render_template('home.html', name=user.f_name)
            except AttributeError:
                session.pop("id")
        return render_template('index.html')

    @app.route("/login/", methods=["GET", "POST"])
    def login():
        wrong = False
        if request.method == "POST":
            try:
                if checkpw(request.form["password"].encode('utf-8'), User.get_user(request.form['id']).pass_hash):
                    session.update({"id": str(request.form["id"])})
                    return redirect(request.args.get('redir', default='/', type=str), 303)
                wrong = True
            except (ValueError, AttributeError, TypeError, KeyError):
                wrong = True
        return render_template('login.html', wrong=wrong, new=False, redir=request.args.get('redir', default='/', type=str))

    @app.post("/logout/")
    def logout():
        session.pop("id", None)
        return redirect("/", 303)

    @app.route("/sign-up/", methods=['GET', 'POST'])
    def sign_up():
        if request.method == 'POST':
            if request.form['password'] == request.form['confirm-password']:
                user = User(request.form['username'], request.form['f-name'], request.form.get('m-name'), request.form['l-name'],
                            request.form['age'], request.form['sex'], hashpw(request.form['password'].encode('utf-8'), gensalt()))
                return render_template("login.html", wrong=False, new=user.username, redir='/')
            return render_template('sign-up.html', match_issue=True)
        return render_template('sign-up.html', match_issue=False)

    @app.route("/records/")
    def records():
        if session.get('id'):
          user = User.get_user(session['id'])
          return render_template('records.html', immunizations=user.immunizations, allergies=user.allergies, meds=user.meds, vitals=user.vitals)
        return redirect('/login/?redir=/records/')

    @app.route("/schedule/")
    def schedule():
        if session.get('id'):
          user = User.get_user(session['id'])
          return render_template('schedule.html', appointments=user.appointments)
        return redirect('/login/?redir=/records/')

    if __name__ == '__main__':
        app.run('0.0.0.0', 443, ssl_context='adhoc')
except:
    print_exc()
    User.close()
    raise SystemExit
