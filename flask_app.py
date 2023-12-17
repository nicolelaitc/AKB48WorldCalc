import os
import sqlite3
from itertools import combinations, product
from tempfile import mkdtemp

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session
from src.forms import *
from src.helpers import *
from src.calculator import *
from src.enum_app import *

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY
Session(app)

csrf = CSRFProtect()
csrf.init_app(app)

# use sqlite3 database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "akb48world.db")
db = sqlite3.connect(db_path, check_same_thread=False)
db.row_factory = sqlite3.Row
cursor = db.cursor()

open("app_log.txt", "w")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """show the import/export to csv option"""
    # ask for log in
    if not session["user_id"]:
        return redirect("/login")
    else:
        # show the import option
        # update entry if duplicate
        # show the export option
        user = cursor.execute(
            "select * from users where id=?", (session["user_id"],)
        ).fetchone()
        username = user["username"]
        return render_template("index.html", username=username)


@app.route("/input", methods=["GET", "POST"])
@login_required
def input():
    user_id = str(session["user_id"])
    """enter each cards manually"""
    themes = get_theme_list(cursor, user_id)
    members = get_member_list(cursor, user_id)
    teams = ["A", "K", "B", "4", "8"]

    skill_targets_list = [target.display_name() for target in SkillTargets]
    skill_types_list = [t.display_name() for t in SkillTypes]

    if request.method == "GET":
        form = InputForm()
        # call the theme list
        return render_template(
            "input.html",
            themes=themes,
            members=members,
            teams=teams,
            skill_targets_list=skill_targets_list,
            skill_types_list=skill_types_list,
            form=form,
        )

    elif request.method == "POST":
        # check the type of data needed
        form = InputForm(request.form)

        form.theme.choices = themes
        form.member.choices = members
        form.team.choices = teams
        form.cheer.choices = members

        if form.validate() == False:
            flash(printErrorMsgs(form.errors))
            return render_template(
                "input.html",
                themes=themes,
                members=members,
                teams=teams,
                skill_targets_list=skill_targets_list,
                skill_types_list=skill_types_list,
                form=form,
            )

        theme = form.theme.data
        if form.theme.data == "(Other)":
            theme = form.theme_other.data
            cursor.execute(
                "insert into themes (user, name) values (?, ?)",
                (user_id, form.theme_other.data),
            )

        member = form.member.data
        if form.member.data == "(Other)":
            member = form.member_other.data
            cursor.execute(
                "insert into members (user,member) values (?, ?)",
                (user_id, form.member_other.data),
            )

        user_id = str(session["user_id"])
        # check duplicate
        duplicate_check = cursor.execute(
            "select * from cards where theme = ? and team = ? and member = ? and user_id = ?",
            (
                theme,
                form.team.data,
                member,
                user_id,
            ),
        ).fetchone()

        if duplicate_check is not None:
            flash("This card is already in the database!")
            return render_template(
                "input.html",
                themes=themes,
                members=members,
                teams=teams,
                skill_targets_list=skill_targets_list,
                skill_types_list=skill_types_list,
                form=form,
            )
        else:
            # insert card data into table
            cursor.execute(
                "INSERT INTO cards (user_id, theme, team, member, singing, dancing , variety, style, skill_type, skill_target, skill_rate, cheer, cheer_skill, cheer_rate, total) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    user_id,
                    theme,
                    form.team.data,
                    member,
                    form.singing.data,
                    form.dancing.data,
                    form.variety.data,
                    form.style.data,
                    SkillTypes.from_display_name(form.skill_type.data),
                    SkillTargets.from_display_name(form.skill_target.data),
                    form.skill_rate.data,
                    form.cheer.data,
                    SkillTypes.from_display_name(form.cheer_skill.data),
                    form.cheer_rate.data,
                    form.total.data,
                ),
            )

            db.commit()
            flash("Your card has been saved!")
            return render_template("input2.html")


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    user_id = str(session["user_id"])
    themes = get_theme_list(cursor, user_id)
    members = get_member_list(cursor, user_id)
    teams = ["A", "K", "B", "4", "8"]

    skill_targets_list = [target.display_name() for target in SkillTargets]
    skill_types_list = [type.display_name() for type in SkillTypes]

    if request.method == "GET":
        card = cursor.execute(
            "select * from cards where id = ? and user_id = ?;",
            (
                request.form.get("id"),
                user_id,
            ),
        ).fetchone()

        form = savedDataToInputForm(card)
        # call the theme list
        return render_template(
            "edit.html",
            themes=themes,
            members=members,
            teams=teams,
            skill_targets_list=skill_targets_list,
            skill_types_list=skill_types_list,
            form=form,
        )
    else:
        form = InputForm(request.form)

        form.theme.choices = themes
        form.member.choices = members
        form.team.choices = teams
        form.cheer.choices = members

        if form.validate() == False:
            error_msg = printErrorMsgs(form.errors)
            flash(error_msg)
            return render_template(
                "input.html",
                themes=themes,
                members=members,
                teams=teams,
                skill_targets_list=skill_targets_list,
                skill_types_list=skill_types_list,
                form=form,
            )
        cursor.execute(
            "update cards set user_id=?, theme=?, team=?, member=?, singing=?, dancing=?, variety=?, style=?, skill_type=?, skill_target=?, skill_rate=?, cheer=?, cheer_skill=?, cheer_rate=?, total=? where id=?",
            (
                user_id,
                form.theme.data,
                form.team.data,
                form.member.data,
                form.singing.data,
                form.dancing.data,
                form.variety.data,
                form.style.data,
                SkillTypes.from_display_name(form.skill_type.data),
                SkillTargets.from_display_name(form.skill_target.data),
                form.skill_rate.data,
                form.cheer.data,
                SkillTypes.from_display_name(form.cheer_skill.data),
                form.cheer_rate.data,
                form.total.data,
                request.form.get("id"),
            ),
        )

        db.commit()

    flash("Your card has been updated!")

    return render_template("edit2.html")


@app.route("/calculator", methods=["GET", "POST"])
@login_required
def calculator():
    user_id = str(session["user_id"])

    today_target_teams = get_today_target_teams()
    today_skills = get_today_skills()
    stages = get_stages()
    opponent_team = get_opponent_team()

    if request.method == "GET":
        form = calculatorForm()

        return render_template(
            "calculator.html",
            form=form,
            today_target_teams=today_target_teams,
            today_skills=today_skills,
            stages=stages,
            opponent_team=opponent_team,
        )
    elif request.method == "POST":
        form = calculatorForm(request.form)

        form.today_skill.choices = today_skills
        form.today_target_team.choices = today_target_teams
        form.stage.choices = stages
        form.opponent.choices = opponent_team

        if form.validate() == False:
            error_msg = printErrorMsgs(form.errors)
            flash(error_msg)
            return render_template(
                "calculator.html",
                form=form,
                today_target_teams=today_target_teams,
                today_skills=today_skills,
                stages=stages,
                opponent_cards=opponent_team,
            )

        # get the data from the form
        form_data_dict = {
            "today_target_team": form.today_target_team.data[-1],
            "today_skill": form.today_skill.data,
            "attributes_weighting": {
                "singing": form.singing.data / 100,
                "dancing": form.dancing.data / 100,
                "variety": form.variety.data / 100,
                "style": form.style.data / 100,
            },
            "today_bonus_rate": form.bonus_rate.data / 100,
            "target": form.target.data,
            "opponent": form.opponent.data,
            "stage": form.stage.data,
            "production": form.production.data,
        }

        cards_raw = cursor.execute(
            "select * from cards where user_id=?", user_id
        ).fetchall()
        cards = [dict(row) for row in cards_raw]

        best_cards, best_stat, best_support, message = calculation(
            cards, form_data_dict
        )
        flash(message)
        if best_cards is None and best_stat is None and message:
            return render_template(
                "calculator.html",
                form=form,
                today_target_teams=today_target_teams,
                today_skills=today_skills,
                stages=stages,
                opponent_cards=opponent_team,
            )
        else:
            for card in best_cards:
                card = convert_to_int(card)
            for card in best_support:
                card = convert_to_int(card)
            best_stat = convert_to_int(best_stat)
            return render_template(
                "calculator_result.html",
                best_stat=best_stat,
                best_card=best_cards,
                best_support=best_support,
            )


@app.route("/card", methods=["GET", "POST"])
@login_required
def card():
    """show the card collection and allow edit/delete"""
    user_id = str(session["user_id"])
    themes = cursor.execute(
        "select name from themes where user = ? or user = 0;", (user_id,)
    ).fetchall()
    themes = [str(item[0]) for item in themes]
    themes.append("(Other)")

    members = cursor.execute(
        "select member from members where user = ? or user = 0;", (user_id,)
    ).fetchall()
    members = [str(item[0]) for item in members]
    members.append("(Others)")

    teams = ["A", "K", "B", "4", "8"]

    skill_targets_list = [
        "Herself",
        "Her Team",
        "All",
        "Opponent TeamA",
        "Opponent Team K",
        "Opponent Team B",
        "Opponent Team 4",
        "Opponent Team 8",
    ]

    skill_types_list = ["singing", "dancing", "variety", "style"]

    if request.method == "GET":
        form = editForm()
        cards = cursor.execute(
            "select * from cards where user_id = ?", (user_id,)
        ).fetchall()

        return render_template("card.html", form=form, cards=cards)

    elif request.method == "POST":
        form = editForm(request.form)

        if form.validate() == False:
            flash("Please select a card!")
            return redirect(request.path)

        id = form.id.data
        check = cursor.execute("select * from cards where id = ?", (id,)).fetchone()
        if len(check) == 0:
            flash("Card ID is invalid!")
            return redirect(request.path)
        else:
            if request.form.get("edit") == "edit":
                card = cursor.execute(
                    "select * from cards where id=?", (id,)
                ).fetchone()

                form = savedDataToInputForm(card)

                return render_template(
                    "edit.html",
                    themes=themes,
                    members=members,
                    teams=teams,
                    skill_targets_list=skill_targets_list,
                    skill_types_list=skill_types_list,
                    form=form,
                    id=id,
                )
            elif request.form.get("delete") == "delete":
                cursor.execute("delete from cards where id=?", (id,))
                flash("Your card has been deleted!")
                return render_template("edit2.html")


"""
@ app.route("/weakness", methods=["GET"])
@ login_required
def weakness():
    table_name = "userID" + str(session["user_id"])
    cardbank = db.execute("select * from ?", table_name)
"""

# show the four card with highest singing, dancing, variety, style
# show the four card with highest(singing+dancing), etc.


def get_today_target_teams():
    return [
        "Team A",
        "Team K",
        "Team B",
        "Team 4",
        "Team 8",
        "All",
    ]


def get_today_skills():
    return ["singing", "dancing", "variety", "style", "All"]


def get_stages():
    return [
        "Main Story",
        "TeamA Story",
        "TeamK Story",
        "TeamB Story",
        "Team4 Story",
        "Team8 Story",
        "SP",
        "VS",
    ]


def get_opponent_team():
    return [
        "No",
        "TeamA",
        "TeamK",
        "TeamB",
        "Team4",
        "Team8",
    ]


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    # cannot use session.clear otherwise it will clear the flash message also
    session["user_id"] = None

    if request.method == "GET":
        form = loginForm()
        return render_template("login.html", form=form)
    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":
        form = loginForm(request.form)

        if form.validate() == False:
            error_msg = printErrorMsgs(form.errors)
            flash(error_msg)
            return render_template("login.html", form=form)

        username = form.username.data
        password = form.password.data
        # Query database for username
        rows = cursor.execute(
            "SELECT username FROM users WHERE username=?", (username,)
        ).fetchone()

        # Ensure username exists and password is correct
        if not rows or not check_password_hash(rows["hash"], password):
            flash("invalid username and/or password")
            return redirect(request.path)

        # Remember which user has logged in
        session["user_id"] = rows["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        form = loginForm()
        return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # -check birthdays -
    # when requested via GET, display registration form
    if request.method == "GET":
        form = registerForm()
        return render_template("register.html", form=form)
    elif request.method == "POST":
        form = registerForm(request.form)
        username, password = form.username.data, form.password.data

        if form.validate() == False:
            error_msg = printErrorMsgs(form.errors)
            flash(error_msg)
            return render_template("register.html", form=form)

        check_duplicate = cursor.execute(
            "SELECT username FROM users WHERE username=?", (username,)
        )

        # any field left ba
        # username being taken
        if len(check_duplicate.fetchall()) != 0:
            flash("The username has been taken.")
            return redirect(request.path)
        # only store the hashed password
        # log user in
        else:
            hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, hash) VALUES(?, ?)",
                (
                    username,
                    hash,
                ),
            )

            db.commit()

            return render_template("index.html")


@app.route("/memberlist", methods=["GET", "POST"])
def memberlist():
    user_id = str(session["user_id"])
    themes_other = cursor.execute(
        "select name from themes where user = ?;", (user_id,)
    ).fetchall()
    themes_other = [str(item[0]) for item in themes_other]

    members_other = cursor.execute(
        "select member from members where user = ?;", (user_id,)
    ).fetchall()
    members_other = [str(item[0]) for item in members_other]

    if request.method == "GET":
        form = memberListForm()

        maxlength = max(len(themes_other), len(members_other))
        return render_template(
            "memberlist.html",
            form=form,
            members_other=members_other,
            themes_other=themes_other,
            maxlength=maxlength,
        )
    else:
        form = memberListForm(request.form)
        user_id = str(session["user_id"])
        if form.validate() == False:
            flash(printErrorMsgs(form.errors))
            return render_template("memberlist.html", form=form)

        item_type = form.item_type.data
        id = form.var.data

        if item_type == "theme":
            # how to retrieve the correct id
            theme_name = themes_other[id - 1]
            cursor.execute(
                "delete from themes where name = ? and user=?", (theme_name, user_id)
            )
        else:
            member_name = members_other[id - 1]
            cursor.execute(
                "delete from members where member = ? and user=?",
                (member_name, user_id),
            )

        db.commit()
        flash("Your chosen choice has been deleted!")

        return render_template(
            "memberlist2.html",
        )
