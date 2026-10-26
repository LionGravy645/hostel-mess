# Hostel Mess Ordering System - website part (Flask)
# Each @app.route is one page or one button on the website.
# The old input() menus are now web pages; the logic lives in mess.py.

import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mess

app = Flask(__name__)
# secret key protects the login cookie - set your own on the server
app.secret_key = os.environ.get("SECRET_KEY", "change-this-to-any-long-random-text")

mess.load_data()


# ---------------- helpers ----------------
def to_int(text):
    # like int(input()), but does not crash on bad input
    try:
        return int(text)
    except (TypeError, ValueError):
        return None


def logged_in_student():
    reg_no = session.get("reg_no")
    if reg_no in mess.students:
        return reg_no
    return None


def show(message):
    # green box for good news, red box for errors
    good_words = ["added", "placed", "updated", "removed", "recharged"]
    kind = "error"
    for w in good_words:
        if w in message.lower():
            kind = "success"
    flash(message, kind)


# ---------------- main menu ----------------
@app.route("/")
def home():
    if logged_in_student():
        return redirect(url_for("student_page"))
    return render_template("home.html", menu=mess.menu)


@app.route("/login", methods=["POST"])
def student_login():
    reg_no = request.form.get("reg_no", "").strip().upper()
    if reg_no in mess.students:
        session["reg_no"] = reg_no
        return redirect(url_for("student_page"))
    flash("Reg No not found. Please register first.", "error")
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        reg_no = request.form.get("reg_no", "").strip().upper()
        name = request.form.get("name", "").strip()
        if reg_no == "" or name == "":
            flash("Please fill in both Reg No and name.", "error")
            return redirect(url_for("register"))
        result = mess.add_student(reg_no, name)
        if result == "Student added":
            session["reg_no"] = reg_no
            flash("Welcome! You start with " + str(mess.MONTHLY_CREDITS) + " credits.", "success")
            return redirect(url_for("student_page"))
        flash(result, "error")
    return render_template("register.html")


# ---------------- student part ----------------
@app.route("/student")
def student_page():
    reg_no = logged_in_student()
    if not reg_no:
        return redirect(url_for("home"))
    return render_template("student.html",
                           reg_no=reg_no,
                           student=mess.students[reg_no],
                           menu=mess.menu,
                           orders=mess.student_orders(reg_no))


@app.route("/order", methods=["POST"])
def make_cart():
    reg_no = logged_in_student()
    if not reg_no:
        return redirect(url_for("home"))

    # one quantity box per menu item
    items = request.form.getlist("item")
    qtys = request.form.getlist("qty")
    cart = []
    for i in range(len(items)):
        qty = to_int(qtys[i])
        if qty is None or qty < 0:
            flash("Quantity must be a whole number.", "error")
            return redirect(url_for("student_page"))
        if qty > 0 and items[i] in mess.menu:
            cart.append([items[i], qty])

    if len(cart) == 0:
        flash("You did not order anything.", "error")
        return redirect(url_for("student_page"))

    session["cart"] = cart
    return redirect(url_for("review_order"))


@app.route("/order/review")
def review_order():
    reg_no = logged_in_student()
    cart = session.get("cart")
    if not reg_no or not cart:
        return redirect(url_for("student_page"))
    # drop anything staff removed while the student was deciding
    cart = [c for c in cart if c[0] in mess.menu]
    lines = []
    for c in cart:
        lines.append({"item": c[0], "qty": c[1], "price": mess.menu[c[0]], "cost": mess.menu[c[0]] * c[1]})
    total = mess.cart_total(cart)
    balance = mess.students[reg_no]["credits"]
    return render_template("review.html", lines=lines, total=total,
                           balance=balance, enough=total <= balance)


@app.route("/order/confirm", methods=["POST"])
def confirm_order():
    reg_no = logged_in_student()
    cart = session.pop("cart", None)
    if not reg_no or not cart:
        return redirect(url_for("student_page"))
    show(mess.place_cart(reg_no, cart))
    return redirect(url_for("student_page"))


@app.route("/order/cancel", methods=["POST"])
def cancel_order():
    session.pop("cart", None)
    flash("Order cancelled.", "error")
    return redirect(url_for("student_page"))


@app.route("/recharge", methods=["POST"])
def student_recharge():
    reg_no = logged_in_student()
    if not reg_no:
        return redirect(url_for("home"))
    amount = to_int(request.form.get("amount"))
    if amount is None:
        flash("Enter a whole number.", "error")
    else:
        show(mess.recharge(reg_no, amount))
    return redirect(url_for("student_page"))


@app.route("/logout")
def logout():
    session.pop("reg_no", None)
    session.pop("cart", None)
    flash("Logged out.", "success")
    return redirect(url_for("home"))


# ---------------- staff part ----------------
@app.route("/staff/login", methods=["GET", "POST"])
def staff_login():
    if request.method == "POST":
        if request.form.get("password") == mess.STAFF_PASSWORD:
            session["staff"] = True
            return redirect(url_for("staff_page"))
        flash("Wrong password!", "error")
    return render_template("staff_login.html")


@app.route("/staff")
def staff_page():
    if not session.get("staff"):
        return redirect(url_for("staff_login"))
    date = request.args.get("date") or mess.today()
    return render_template("staff.html",
                           menu=mess.menu,
                           students=mess.students,
                           summary=mess.daily_summary(date),
                           is_today=(date == mess.today()),
                           monthly=mess.MONTHLY_CREDITS)


@app.route("/staff/item/add", methods=["POST"])
def staff_add_item():
    if not session.get("staff"):
        return redirect(url_for("staff_login"))
    price = to_int(request.form.get("price"))
    if price is None:
        flash("Price must be a whole number.", "error")
    else:
        show(mess.add_item(request.form.get("name", "").strip(), price))
    return redirect(url_for("staff_page"))


@app.route("/staff/item/price", methods=["POST"])
def staff_change_price():
    if not session.get("staff"):
        return redirect(url_for("staff_login"))
    price = to_int(request.form.get("price"))
    if price is None:
        flash("Price must be a whole number.", "error")
    else:
        show(mess.change_price(request.form.get("item"), price))
    return redirect(url_for("staff_page"))


@app.route("/staff/item/remove", methods=["POST"])
def staff_remove_item():
    if not session.get("staff"):
        return redirect(url_for("staff_login"))
    show(mess.remove_item(request.form.get("item")))
    return redirect(url_for("staff_page"))


@app.route("/staff/monthly", methods=["POST"])
def staff_monthly():
    if not session.get("staff"):
        return redirect(url_for("staff_login"))
    show(mess.add_monthly_credits())
    return redirect(url_for("staff_page"))


@app.route("/staff/logout")
def staff_logout():
    session.pop("staff", None)
    flash("Logged out.", "success")
    return redirect(url_for("home"))


# ---------------- run on your own computer ----------------
if __name__ == "__main__":
    app.run(debug=True)
