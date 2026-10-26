# Hostel Mess Ordering System - logic part
# Menu | Orders per student | Credits | Daily sales summary
#
# This is your original logic. The only changes for the website:
#   - functions RETURN results instead of print()/input()
#   - data is saved to data.json so it is not lost when the server restarts

import datetime
import json
import os
import threading

# ---------------- settings ----------------
STAFF_PASSWORD = os.environ.get("STAFF_PASSWORD", "admin123")
MONTHLY_CREDITS = 9000

# India time (servers usually run on UTC time)
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

# data.json is kept next to this file
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
lock = threading.Lock()   # stops two orders from writing the file at the same moment

# ---------------- data ----------------
# menu: item name -> price
menu = {
    "Veg Thali": 50,
    "Chapati Combo": 40,
    "Masala Dosa": 45,
    "Idli": 25,
    "Tea": 10
}

# students: reg no -> name and credits
students = {
    "26BIT0005": {"name": "Yatharth Sharma", "credits": 9000},
    "26BIT0025": {"name": "Arnav Sanjeev Prakash", "credits": 9000},
    "26BIT0037": {"name": "Aryan Kumar", "credits": 9000}
}

# orders: list that keeps every order together
orders = []


# ---------------- saving and loading ----------------
def save_data():
    data = {"menu": menu, "students": students, "orders": orders}
    temp_file = DATA_FILE + ".tmp"
    with open(temp_file, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(temp_file, DATA_FILE)   # swap in the new file in one step


def load_data():
    # first run: no file yet, so save the starting data above
    if not os.path.exists(DATA_FILE):
        save_data()
        return
    with open(DATA_FILE) as f:
        data = json.load(f)
    # .clear() + .update() keeps the same dictionaries/lists that app.py uses
    menu.clear()
    menu.update(data["menu"])
    students.clear()
    students.update(data["students"])
    orders.clear()
    orders.extend(data["orders"])


# ---------------- functions ----------------
def add_student(reg_no, name):
    with lock:
        if reg_no in students:
            return "Student already exists"
        students[reg_no] = {"name": name, "credits": MONTHLY_CREDITS}
        save_data()
    return "Student added"


def get_item_by_number(num):
    # turns menu number into item name
    items = list(menu.keys())
    if num >= 1 and num <= len(items):
        return items[num - 1]
    return None


def cart_total(cart):
    # cart is a list of [item, qty]
    total = 0
    for c in cart:
        total += menu[c[0]] * c[1]
    return total


def place_cart(reg_no, cart):
    # places every food in the cart (same as the end of student_order)
    with lock:
        for c in cart:
            if c[0] not in menu:
                return "Sorry, " + c[0] + " is no longer on the menu"
        total = cart_total(cart)
        student = students[reg_no]
        if total > student["credits"]:
            return "Not enough credits! Please recharge."
        now = datetime.datetime.now(IST)
        for c in cart:
            cost = menu[c[0]] * c[1]
            student["credits"] -= cost
            orders.append({"reg_no": reg_no,
                           "item": c[0],
                           "qty": c[1],
                           "cost": cost,
                           "date": str(now.date()),
                           "time": now.strftime("%H:%M:%S")})
        save_data()
    return "Order placed!"


def student_orders(reg_no):
    result = []
    for o in orders:
        if o["reg_no"] == reg_no:
            result.append(o)
    result.reverse()   # newest first
    return result


def recharge(reg_no, amount):
    if amount <= 0:
        return "Amount must be more than 0"
    with lock:
        students[reg_no]["credits"] += amount
        save_data()
    return "Recharged. New balance: " + str(students[reg_no]["credits"])


def add_monthly_credits():
    # run at the start of every month
    with lock:
        for reg_no in students:
            students[reg_no]["credits"] += MONTHLY_CREDITS
        save_data()
    return "Added " + str(MONTHLY_CREDITS) + " credits to all students."


def add_item(name, price):
    if name == "":
        return "Item name cannot be empty"
    if price <= 0:
        return "Price must be more than 0"
    with lock:
        if name in menu:
            return "Item already exists!"
        menu[name] = price
        save_data()
    return "Item added."


def change_price(item, price):
    if price <= 0:
        return "Price must be more than 0"
    with lock:
        if item not in menu:
            return "Wrong item!"
        menu[item] = price
        save_data()
    return "Price updated."


def remove_item(item):
    with lock:
        if item not in menu:
            return "Wrong item!"
        del menu[item]
        save_data()
    return "Item removed."


def today():
    return str(datetime.datetime.now(IST).date())


def daily_summary(date):
    # same counting as before, but returns the numbers for the web page
    item_qty = {}
    item_amount = {}
    total_orders = 0
    total_items = 0
    total_sales = 0

    for o in orders:
        if o["date"] == date:
            total_orders += 1
            total_items += o["qty"]
            total_sales += o["cost"]
            if o["item"] in item_qty:
                item_qty[o["item"]] += o["qty"]
                item_amount[o["item"]] += o["cost"]
            else:
                item_qty[o["item"]] = o["qty"]
                item_amount[o["item"]] = o["cost"]

    rows = []
    for item in item_qty:
        rows.append({"item": item, "qty": item_qty[item], "amount": item_amount[item]})

    return {"date": date,
            "rows": rows,
            "total_orders": total_orders,
            "total_items": total_items,
            "total_sales": total_sales}
