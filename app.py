from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import or_

from database import session
from models import Spot
from services.ai_service import generate_text
from services.city_api import get_city_display_name

app = Flask(__name__)

CATEGORIES = ["politics", "restaurant", "fast_food", "dessert"]  # категории на типови на локали


@app.get("/")
def home():
    return render_template("index.html")  # прикажување на почетната страна


@app.get("/spots")
def spots_list():
    q = (request.args.get("q") or "").strip()  # ни овозможува пребарување според име или град
    category = (request.args.get("category") or "").strip()  # пребарување според категорија

    query = session.query(Spot)

    if q:  # search функционалноста
        like = f"%{q}%"
        query = query.filter(
            or_(
                Spot.name.ilike(like),
                Spot.city_query.ilike(like),
                Spot.city_full_name.ilike(like),
            )
        )

    if category:  # филтрирање според категорија
        query = query.filter(Spot.category == category)

    spots = query.order_by(Spot.created_at.desc()).all()  # ги подредуваме според последно креирано место
    session.close()

    return render_template(
        "spots_list.html",
        spots=spots,
        q=q,
        category=category,
        categories=CATEGORIES,
    )


@app.route("/spots/new", methods=["GET", "POST"])
def spots_new():
    # креираме ново место
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        city_query = (request.form.get("city_query") or "").strip()
        category = (request.form.get("category") or "").strip()
        price_level_raw = (request.form.get("price_level") or "").strip()
        notes = (request.form.get("notes") or "").strip()

        if not name or not city_query or not category:
            flash("Име, град и категорија се задолжителни.", "error")
            return render_template("spot_form.html", spot=None, categories=CATEGORIES)

        price_level = None
        if price_level_raw:
            try:
                price_level = int(price_level_raw)
            except ValueError:
                price_level = None

        city_full_name = get_city_display_name(city_query)  # го земаме целосното име на градот со помош на АПИ-то

        spot = Spot(
            name=name,
            city_query=city_query,
            city_full_name=city_full_name,
            category=category,
            price_level=price_level,
            notes=notes or None,
        )
        session.add(spot)
        session.commit()
        return redirect(url_for("spot_detail", spot_id=spot.id))

    return render_template("spot_form.html", spot=None, categories=CATEGORIES)


@app.get("/spots/<int:spot_id>")
def spot_detail(spot_id: int):
    # доколку постои место со тоа ИД ги прикажуваме деталите за него, доколку не постои - прикажуваме 404
    spot = session.get(Spot, spot_id)
    if not spot:
        return "Не постои место со ова ИД", 404
    return render_template("spot_detail.html", spot=spot, categories=CATEGORIES)


@app.route("/spots/<int:spot_id>/edit", methods=["GET", "POST"])
def spot_edit(spot_id: int):
    # ги едитираме деталите за местото на сличен начин како што креиравме ново место
    spot = session.get(Spot, spot_id)
    if not spot:
        return "Не постои место со ова ИД", 404

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        city_query = (request.form.get("city_query") or "").strip()
        category = (request.form.get("category") or "").strip()
        price_level_raw = (request.form.get("price_level") or "").strip()
        notes = (request.form.get("notes") or "").strip()

        if not name or not city_query or not category:
            flash("Име, град и категорија се задолжителни.", "error")
            return render_template("spot_form.html", spot=spot, categories=CATEGORIES)

        price_level = None
        if price_level_raw:
            try:
                price_level = int(price_level_raw)
            except ValueError:
                price_level = None

        if city_query != spot.city_query:
            spot.city_full_name = get_city_display_name(city_query)

        spot.name = name
        spot.city_query = city_query
        spot.category = category
        spot.price_level = price_level
        spot.notes = notes or None

        session.commit()
        return redirect(url_for("spot_detail", spot_id=spot.id))

    return render_template("spot_form.html", spot=spot, categories=CATEGORIES)


@app.post("/spots/<int:spot_id>/delete")
def spot_delete(spot_id: int):
    # го бришеме локалот од база доколку постои
    spot = session.get(Spot, spot_id)
    if not spot:
        return "Не постои место со ова ИД", 404
    session.delete(spot)
    session.commit()
    return redirect(url_for("spots_list"))


# Следните 2 рути/endpoints се со примена на АИ, поточно gemini

@app.post("/ai/rewrite/<int:spot_id>")
def ai_rewrite(spot_id):
    spot = session.get(Spot, spot_id)
    if not spot:
        return "Не постои место со ова ИД", 404

    if not spot.notes:
        return redirect(url_for("spot_detail", spot_id=spot.id))
        # при креирање на локалот мора да имаме оставено notes за да има AI што да rewrite-не,
    # доколку нема не враќа повторно на детаил страната

    prompt = (
        "Rewrite this short description in Macedonian. "
        "Keep it friendly and short (2-3 sentences). "
        "Do not invent facts."
        "Give me directly the description without any other additional things. Text: \n"
        f"{spot.notes}"
    )  # ова се некои насоки што ги праќаме на gemini моделот

    result = generate_text(prompt)
    spot.ai_description = result  # го зачувуваме резултатот од AI во база
    session.commit()

    return redirect(url_for("spot_detail", spot_id=spot.id))
    # правиме „refresh“ на страната за да ги видиме новите промени (резултатот од АИ)


@app.post("/ai/tags/<int:spot_id>")
def ai_tags(spot_id):
    spot = session.get(Spot, spot_id)
    if not spot:
        return "Не постои место со ова ИД", 404

    prompt = (
        "Suggest 6-8 short tags in Macedonian, comma-separated. "
        "Do not use hashtags (#).\n\n"
        f"Name: {spot.name}\n"
        f"Category: {spot.category}\n"
        f"City: {spot.city_full_name or spot.city_query}\n"
        f"Notes: {spot.notes or ''}"
    )  # ова се некои насоки што ги праќаме на gemini моделот

    result = generate_text(prompt)
    spot.tags = result  # го зачувуваме резултатот од AI во база
    session.commit()

    return redirect(url_for("spot_detail", spot_id=spot.id))


# правиме „refresh“ на страната за да ги видиме новите промени (резултатот од АИ)

if __name__ == "__main__":
    app.run(debug=True)
