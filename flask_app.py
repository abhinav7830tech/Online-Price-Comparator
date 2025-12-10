from flask import Flask, render_template, request, redirect, session, url_for, flash
from datetime import timedelta

# --- FIX 1: Import 'get_user_collection' so the profile page works ---
from streamlit_version_backup import authenticate_user, register_user, fetch_prices_from_perplexity, TARGET_STORES, get_user_collection

app = Flask(__name__)
app.secret_key = "supersecretkey123"
app.permanent_session_lifetime = timedelta(days=7)


@app.route("/")
def home():
    if "user_email" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        ok, msg = authenticate_user(email, password)
        if ok:
            session.permanent = True        # <── FIXED
            session["user_email"] = email
            return redirect(url_for("dashboard"))
        flash(msg, "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        if password != confirm:
            flash("Passwords do not match", "danger")
        else:
            ok, msg = register_user(email, password)
            flash(msg, "success" if ok else "danger")

    return render_template("register.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_email" not in session:
        return redirect("/login")

    product_title = None
    store_data = None

    if request.method == "POST":
        query = request.form.get("query", "")
        if query.strip():
            data, err = fetch_prices_from_perplexity(query)
            if err:
                flash(err, "danger")
            else:
                product_title = data.get("product_title")
                store_data = data.get("stores")

    return render_template(
        "dashboard.html",
        title="Dashboard",
        product_title=product_title,
        store_data=store_data
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not session.get("user_email"):
        return redirect("/login")

    # FIX 2: Ensure get_user_collection is imported at the top of the file
    users = get_user_collection()
    
    # FIX 3: Safety check - handle if user is not found in DB
    user = users.find_one({"email": session["user_email"]})
    
    if not user:
        # Session exists but user doesn't (database mismatch). Log them out.
        session.pop("user_email", None)
        flash("User not found. Please login again.", "danger")
        return redirect(url_for("login"))

    phone = user.get("phone", "")

    if request.method == "POST":
        new_phone = request.form.get("phone")
        users.update_one({"email": session["user_email"]}, {"$set": {"phone": new_phone}})
        phone = new_phone
        flash("Profile updated successfully!", "success")

    return render_template("profile.html", phone=phone)


@app.route("/logout")
def logout():
    session.pop("user_email", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)