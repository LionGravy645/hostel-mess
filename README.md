# Hostel Mess Ordering System — Website

Your original Python mess system, now running as a website with Flask.

## What's in the folder

| File | What it does |
|---|---|
| `mess.py` | Your original logic (menu, students, orders, credits, daily summary). Functions now **return** results instead of using `print()`/`input()`, and everything is saved to `data.json`. |
| `app.py` | The website. Each `@app.route(...)` is one page or one button. This replaces the old `while True` menus. |
| `templates/` | The HTML pages (home, register, student, order review, staff login, staff dashboard). |
| `static/style.css` | The look of the site. |
| `data.json` | Created automatically the first time the app runs. Holds all menu, student and order data. |

### How the old menus map to the website

| Old terminal menu | On the website |
|---|---|
| Main menu → 1. Student login | Home page, Reg No box |
| Main menu → 2. New student registration | "Register as a new student" link |
| Main menu → 3. Staff login | "Staff" link at top right (password `admin123`) |
| Student → View menu / Place order | Quantity boxes next to each item, then "Review order" |
| Student → Confirm order? (y/n) | Review page with "Confirm order" and "Cancel" buttons |
| Student → Check balance / My orders / Recharge | All shown on the student page |
| Staff → Add item / Change price / Remove item | Menu card on the staff dashboard |
| Staff → Today's / another day's sales summary | Sales summary card with a date picker |
| Staff → View all students / Add monthly credits | Students card on the staff dashboard |

---

## 1. Run it on your Mac first

Open **Terminal** (Cmd + Space, type "Terminal").

```bash
cd ~/Downloads/hostel_mess_web      # wherever you unzipped the folder
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open **http://127.0.0.1:5000** in your browser. Press `Ctrl + C` in Terminal to stop.

Next time you only need `cd ...`, `source venv/bin/activate` and `python3 app.py`.

---

## 2. Put it online for free (PythonAnywhere)

Your site will live at `https://YOUR-USERNAME.pythonanywhere.com`.

**a. Create an account.** Sign up for a free "Beginner" account at pythonanywhere.com. Your username becomes part of the web address.

**b. Upload the project.**
1. Go to the **Files** tab and upload `hostel_mess_web.zip`.
2. Go to **Consoles → Bash** and run:
   ```bash
   unzip hostel_mess_web.zip
   cd hostel_mess_web
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

**c. Create the web app.**
1. **Web** tab → **Add a new web app** → Next.
2. Choose **Manual configuration** (not the "Flask" option — that one starts a blank app).
3. Choose **Python 3.11** (same version as above).
4. In the **Virtualenv** section, enter:
   `/home/YOUR-USERNAME/hostel_mess_web/venv`

**d. Point it at your app.** On the Web tab, click the **WSGI configuration file** link. Delete everything in it and paste this (put in your username and your own secret values):

```python
import os
import sys

project = "/home/YOUR-USERNAME/hostel_mess_web"
if project not in sys.path:
    sys.path.insert(0, project)

# change these two before going live
os.environ["SECRET_KEY"] = "type-any-long-random-sentence-here"
os.environ["STAFF_PASSWORD"] = "choose-a-new-staff-password"

from app import app as application
```

Click **Save**.

**e. Go live.** Back on the **Web** tab, click the green **Reload** button, then open `https://YOUR-USERNAME.pythonanywhere.com`.

If the page shows an error, open the **Error log** link on the Web tab — the last lines say what went wrong.

**Keeping it running:** free web apps have an expiry date shown on the Web tab. Click the button there to extend it before it runs out.

**Updating the site later:** upload the changed file in the Files tab (into `hostel_mess_web/`), then click **Reload** on the Web tab.

---

## Things to know before sharing the link publicly

- **Change the staff password.** `admin123` is in your original code, so anyone who sees it can open the staff dashboard. Set `STAFF_PASSWORD` in the WSGI file as shown above.
- **Student login is Reg No only**, same as the original program. Anyone who knows a Reg No can log in as that student. Adding a PIN or password per student would fix this.
- **Recharge is free**, same as the original: students can add any amount to their own balance. In a real mess you'd move "Recharge" to the staff dashboard.
- **Backups:** all data is in `data.json`. Download it from the Files tab now and then to keep a copy.
- **Resetting everything:** stop the app, delete `data.json`, and reload — it starts again from the menu and students written in `mess.py`.
