from flask import Flask, render_template, request, redirect, url_for, flash, session as flask_session
from sqlalchemy import or_

from database import SessionLocal
from database import session
from models import Poll,Option,Vote,User
from services.ai_service import generate_text
from services.city_api import get_city_display_name

app = Flask(__name__)
app.secret_key = 'Helloiamjakovandiamstudyinginsemostodayis352026at4am'

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/polls")
def polls():
    query = session.query(Poll).join(Option)
    polls = query.order_by(Poll.created_at.desc()).all()
    return render_template(
        "polls.html",
        polls=polls,)


@app.route("/polls/<int:id>", methods=["GET", "POST"])
def poll(id):
    poll_data = session.get(Poll, id)
    if not poll_data:
        return "Poll not found", 404

    if request.method == "POST":
        voted = session.query(Vote).where(Vote.poll_id == id, Vote.user_id == 1).first()
        if voted:
            flash("You have already voted!")
            return render_template("poll.html", poll=poll_data)
        option_id = request.form.get("voting")
        if option_id:
            option = session.get(Option, int(option_id))
            if option:
                option.votes_total += 1
                #current_user_id = flask_session.get("user_id")
                new_vote = Vote(poll_id=id, option_id=option.id, user_id=1)

                session.add(new_vote)
                session.commit()

                flash("Thank you for voting!")

    return render_template("poll.html", poll=poll_data)

@app.route("/polls/new/2", methods=["GET", "POST"])
def polls_new():
    if request.method == "POST":
        name = (request.form.get("name"))
        description = (request.form.get("description"))
        category = (request.form.get("category"))
        privacy = (request.form.get("privacy"))
        option1name = (request.form.get("option1name"))
        option2name = (request.form.get("option2name"))

        if not name or not description or not category or not privacy:
            flash("Please fill all the fields.")
            return render_template("pollcreate.html")

        poll1 = Poll(
            name = name,
            description = description,
            category = category,
            privacy = int(privacy),
            # current_user_id = flask_session.get("user_id")
            user_id = 1,
        )
        session.add(poll1)
        session.commit()

        option1 = Option(optionname=option1name, poll_id=poll1.id)
        option2 = Option(optionname=option2name, poll_id=poll1.id)
        session.add(option1)
        session.add(option2)
        session.commit()
        flash("Poll created!")


    return render_template("pollcreate.html")

@app.route("/users/new", methods=["GET", "POST"])
def users_new():
    if request.method == "POST":
        username = (request.form.get("username"))
        description = (request.form.get("description"))
        email = (request.form.get("email"))
        password = (request.form.get("password"))
        if not username or not email or not password:
            flash("Please fill all the fields.")
            return render_template("newuser.html")
        active = session.query(User).where(User.username == username).first()
        if active:
            flash("Username already exists!")
            return render_template("newuser.html")
        user = User(username=username, email=email, password=password, description=description)
        session.add(user)
        session.commit()
        flash("User created!")
        session.add(user)
        session.commit()
        flask_session["user_id"] = user.id
        flask_session["username"] = user.username
    return render_template("newuser.html")


if __name__ == "__main__":
    app.run(debug=True)




























































