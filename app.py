from flask import Flask, render_template, request, redirect, url_for, flash, session as flask_session

from database import session
from models import Poll, Option, Vote, User
from services.ai_service import generate_text
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET", "").strip()


@app.get("/")
def polls():
    query = session.query(Poll)
    all_polls = query.order_by(Poll.created_at.desc()).where(Poll.privacy != 1).all()
    return render_template("polls.html", polls=all_polls)


@app.route("/polls/<int:id>", methods=["GET", "POST"])
def poll(id):
    poll_data = session.get(Poll, id)
    if not poll_data:
        return "Poll not found", 404

    current_user_id = flask_session.get("user_id")
    if not current_user_id:
        flash("Login first!")
        return redirect(url_for("users_login"))

    if request.method == "POST":
        voted = session.query(Vote).where(Vote.poll_id == id, Vote.user_id == current_user_id).first()
        if voted:
            flash("You have already voted!")
            return redirect(url_for("poll", id=id))

        option_id = request.form.get("voting")
        if option_id:
            option = session.get(Option, int(option_id))
            if option:
                option.votes_total += 1
                new_vote = Vote(poll_id=id, option_id=option.id, user_id=current_user_id)
                session.add(new_vote)
                session.commit()
                flash("Thank you for voting!")
                return redirect(url_for("poll", id=id))

    return render_template("poll.html", poll=poll_data)

@app.route("/polls/new", methods=["GET", "POST"])
def polls_choose():
    current_user_id = flask_session.get("user_id")
    if not current_user_id:
        flash("Login first!")
        return redirect(url_for("users_login"))
    else:
        return render_template("choosesize.html")
@app.route("/polls/new/2", methods=["GET", "POST"])
def polls_new():
    current_user_id = flask_session.get("user_id")
    if not current_user_id:
        flash("Login first!")
        return redirect(url_for("users_login"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        category = request.form.get("category")
        privacy = request.form.get("privacy")
        image = request.form.get("image")
        option1name = request.form.get("option1name")
        option2name = request.form.get("option2name")

        if not name or not description or not category or not privacy:
            flash("Please fill all the fields.")
            return redirect(url_for("polls_new"))

        poll1 = Poll(
            name=name,
            description=description,
            category=category,
            privacy=int(privacy),
            image=image,
            user_id=current_user_id,
        )
        session.add(poll1)
        session.commit()

        option1 = Option(optionname=option1name, poll_id=poll1.id)
        option2 = Option(optionname=option2name, poll_id=poll1.id)
        session.add(option1)
        session.add(option2)
        session.commit()

        if poll1.privacy == 1:
            private_link = url_for('poll', id=poll1.id, _external=True)
            flash(f"Poll created privately! Share this link with others: {private_link}")
        else:
            flash("Poll created successfully!")
        return redirect(url_for("polls"))

    return render_template("pollcreate.html")


@app.route("/users/new", methods=["GET", "POST"])
def users_new():
    if flask_session.get("user_id"):
        return redirect(url_for("polls"))

    if request.method == "POST":
        username = request.form.get("username")
        description = request.form.get("description")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            flash("Please fill all the fields.")
            return redirect(url_for("users_new"))

        active = session.query(User).where(User.username == username).first()
        active2 = session.query(User).where(User.email == email).first()

        if active or active2:
            flash("Username or Email already exists!")
            return redirect(url_for("users_new"))

        user = User(username=username, email=email, password=password, description=description)
        session.add(user)
        session.commit()

        flash("User created!")
        flask_session["user_id"] = user.id
        flask_session["username"] = user.username
        flask_session.permanent = True
        return redirect(url_for("polls"))

    return render_template("newuser.html")


@app.route("/users/login", methods=["GET", "POST"])
def users_login():
    if flask_session.get("user_id"):
        return redirect(url_for("polls"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = session.query(User).filter(User.username == username).first()

        if not username or not password:
            flash("All fields are required.")
            return redirect(url_for("users_login"))

        if user and user.password == password:
            flask_session["user_id"] = user.id
            flask_session["username"] = user.username
            flask_session.permanent = True
            flash(f"Welcome back, {user.username}!")
            return redirect(url_for("polls"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("users_login"))

    return render_template("existinguser.html")


@app.route("/users/logout")
def users_logout():
    flask_session.clear()
    flash("You have been logged out.")
    return redirect(url_for("polls"))

@app.route("/polls/new/3", methods=["GET", "POST"])
def polls_new3():
    current_user_id = flask_session.get("user_id")
    if not current_user_id:
        flash("Login first!")
        return redirect(url_for("users_login"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        category = request.form.get("category")
        privacy = request.form.get("privacy")
        image = request.form.get("image")
        option1name = request.form.get("option1name")
        option2name = request.form.get("option2name")
        option3name = request.form.get("option3name")

        if not name or not description or not category or not privacy:
            flash("Please fill all the fields.")
            return redirect(url_for("polls_new"))

        poll1 = Poll(
            name=name,
            description=description,
            category=category,
            privacy=int(privacy),
            image=image,
            user_id=current_user_id,
        )
        session.add(poll1)
        session.commit()

        option1 = Option(optionname=option1name, poll_id=poll1.id)
        option2 = Option(optionname=option2name, poll_id=poll1.id)
        option3 = Option(optionname=option3name, poll_id=poll1.id)
        session.add(option1)
        session.add(option2)
        session.add(option3)
        session.commit()

        if poll1.privacy == 1:
            private_link = url_for('poll', id=poll1.id, _external=True)
            flash(f"Poll created privately! Share this link with others: {private_link}")
        else:
            flash("Poll created successfully!")
        return redirect(url_for("polls"))

    return render_template("pollcreate3.html")

@app.route("/polls/new/4", methods=["GET", "POST"])
def polls_new4():
    current_user_id = flask_session.get("user_id")
    if not current_user_id:
        flash("Login first!")
        return redirect(url_for("users_login"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        category = request.form.get("category")
        privacy = request.form.get("privacy")
        image = request.form.get("image")
        option1name = request.form.get("option1name")
        option2name = request.form.get("option2name")
        option3name = request.form.get("option3name")
        option4name = request.form.get("option4name")

        if not name or not description or not category or not privacy:
            flash("Please fill all the fields.")
            return redirect(url_for("polls_new4"))

        poll1 = Poll(
            name=name,
            description=description,
            category=category,
            privacy=int(privacy),
            image=image,
            user_id=current_user_id,
        )
        session.add(poll1)
        session.commit()

        option1 = Option(optionname=option1name, poll_id=poll1.id)
        option2 = Option(optionname=option2name, poll_id=poll1.id)
        option3 = Option(optionname=option3name, poll_id=poll1.id)
        option4 = Option(optionname=option4name, poll_id=poll1.id)
        session.add(option1)
        session.add(option2)
        session.add(option3)
        session.add(option4)
        session.commit()

        if poll1.privacy == 1:
            private_link = url_for('poll', id=poll1.id, _external=True)
            flash(f"Poll created privately! Share this link with others: {private_link}")
        else:
            flash("Poll created successfully!")
        return redirect(url_for("polls"))

    return render_template("pollcreate4.html")

@app.route("/polls/new/5", methods=["GET", "POST"])
def polls_new5():
    current_user_id = flask_session.get("user_id")
    if not current_user_id:
        flash("Login first!")
        return redirect(url_for("users_login"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        category = request.form.get("category")
        privacy = request.form.get("privacy")
        image = request.form.get("image")
        option1name = request.form.get("option1name")
        option2name = request.form.get("option2name")
        option3name = request.form.get("option3name")
        option4name = request.form.get("option4name")
        option5name = request.form.get("option5name")

        if not name or not description or not category or not privacy:
            flash("Please fill all the fields.")
            return redirect(url_for("polls_new5"))

        poll1 = Poll(
            name=name,
            description=description,
            category=category,
            privacy=int(privacy),
            image=image,
            user_id=current_user_id,
        )
        session.add(poll1)
        session.commit()

        option1 = Option(optionname=option1name, poll_id=poll1.id)
        option2 = Option(optionname=option2name, poll_id=poll1.id)
        option3 = Option(optionname=option3name, poll_id=poll1.id)
        option4 = Option(optionname=option4name, poll_id=poll1.id)
        option5 = Option(optionname=option5name, poll_id=poll1.id)
        session.add(option1)
        session.add(option2)
        session.add(option3)
        session.add(option4)
        session.add(option5)
        session.commit()

        if poll1.privacy == 1:
            private_link = url_for('poll', id=poll1.id, _external=True)
            flash(f"Poll created privately! Share this link with others: {private_link}")
        else:
            flash("Poll created successfully!")
        return redirect(url_for("polls"))

    return render_template("pollcreate5.html")

@app.route("/polls/new/6", methods=["GET", "POST"])
def polls_new6():
    current_user_id = flask_session.get("user_id")
    if not current_user_id:
        flash("Login first!")
        return redirect(url_for("users_login"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        category = request.form.get("category")
        privacy = request.form.get("privacy")
        image = request.form.get("image")
        option1name = request.form.get("option1name")
        option2name = request.form.get("option2name")
        option3name = request.form.get("option3name")
        option4name = request.form.get("option4name")
        option5name = request.form.get("option5name")
        option6name = request.form.get("option6name")

        if not name or not description or not category or not privacy:
            flash("Please fill all the fields.")
            return redirect(url_for("polls_new6"))

        poll1 = Poll(
            name=name,
            description=description,
            category=category,
            privacy=int(privacy),
            image=image,
            user_id=current_user_id,
        )
        session.add(poll1)
        session.commit()

        option1 = Option(optionname=option1name, poll_id=poll1.id)
        option2 = Option(optionname=option2name, poll_id=poll1.id)
        option3 = Option(optionname=option3name, poll_id=poll1.id)
        option4 = Option(optionname=option4name, poll_id=poll1.id)
        option5 = Option(optionname=option5name, poll_id=poll1.id)
        option6 = Option(optionname=option6name, poll_id=poll1.id)
        session.add(option1)
        session.add(option2)
        session.add(option3)
        session.add(option4)
        session.add(option5)
        session.add(option6)
        session.commit()

        if poll1.privacy == 1:
            private_link = url_for('poll', id=poll1.id, _external=True)
            flash(f"Poll created privately! Share this link with others: {private_link}")
        else:
            flash("Poll created successfully!")
        return redirect(url_for("polls"))

    return render_template("pollcreate6.html")


@app.route("/users/settings", methods=["GET", "POST"])
def users_settings():
    current_user_id = flask_session.get("user_id")
    if not current_user_id:
        flash("Login first!")
        return redirect(url_for("users_login"))

    user = session.get(User, current_user_id)

    if request.method == "POST":
        new_username = request.form.get("username")
        new_email = request.form.get("email")
        new_password = request.form.get("password")
        new_description = request.form.get("description")

        if new_username:
            if new_username != user.username:
                existing_user = session.query(User).filter(User.username == new_username).first()
                if existing_user:
                    flash("Username is already taken!")
                    return redirect(url_for("users_settings"))
                else:
                    user.username = new_username

        if new_email:
            if new_email != user.email:
                existing_email = session.query(User).filter(User.email == new_email).first()
                if existing_email:
                    flash("Email is already registered to another account!")
                    return redirect(url_for("users_settings"))
                else:
                    user.email = new_email

        if new_description:
            user.description = new_description

        if new_password:
            user.password = new_password

        session.commit()

        flask_session["username"] = user.username

        flash("Settings updated successfully!")
        return redirect(url_for("polls"))

    return render_template("usersettings.html", user=user)

@app.route("/users/<int:user_id>", methods=["GET", "POST"])
def userview(user_id):
    polls = session.query(Poll).filter(Poll.user_id == user_id, Poll.privacy != 1).order_by(Poll.created_at.desc()).all()
    user = session.get(User, user_id)
    if not user:
        return "User not found", 404
    return render_template("user.html", user=user, polls=polls)

@app.route("/polls/<int:id>/ai", methods=["GET", "POST"])
def pollai(id):
    poll_data = session.get(Poll, id)
    if not poll_data:
        return "Poll not found", 404

    current_user_id = flask_session.get("user_id")
    if not current_user_id:
        flash("Login first!")
        return redirect(url_for("users_login"))

    prompt = (
        "Give me a direct, light statistical analysis in 1 medium-short paragraph on the data of this poll. Make it user oriented, for a polling website. Ensure all facts are true to the data. Use only plain text, with no text effects(bold, italic, etc...). Give reasons as to why these polls might be giving these outcomes, and a future prediction in 2 sentences. Make it interesting, but still professional."
        f"Poll question: {poll_data.name}\n"  
        f"Category: {poll_data.category}\n"
        f"Options: {[(opt.optionname, opt.votes_total) for opt in poll_data.options]}\n"
        f"Description: {poll_data.description}"
    )

    result = generate_text(prompt)

    return render_template("pollai.html", poll=poll_data, result=result)


@app.route("/pollssearchcat", methods=["GET", "POST"])
def pollssearchcat():
    if request.method == "POST":
        selected_category = request.form.get("category")
        results = session.query(Poll).filter(Poll.category == selected_category, Poll.privacy != 1).all()
        return render_template("catsort.html", polls=results, category=selected_category)
    return render_template("catsort.html", polls=[])


@app.route("/pollssearchexact", methods=["GET", "POST"])
def pollssearchexact():
    if request.method == "POST":
        search_query = request.form.get("poll_name")
        results = session.query(Poll).filter(Poll.name.contains(search_query), Poll.privacy != 1).all()
        return render_template("exactsort.html", polls=results, query=search_query)
    return render_template("exactsort.html", polls=[])

if __name__ == "__main__":
    app.run(debug=True)


