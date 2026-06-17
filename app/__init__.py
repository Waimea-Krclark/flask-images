#===========================================================
# APP NAME HERE
# By YOUR NAME HERE
#===========================================================

from flask import Flask, request, session, render_template, flash, redirect, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from os import getenv
from io import BytesIO
import html
from app.helpers import *
import uuid
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')


# Create the app
app = Flask(__name__)


#===========================================================
# App Routes Handlers
#===========================================================

#-----------------------------------------------------------
# Welcome page
#-----------------------------------------------------------
@app.get("/")
def show_welcome():
    return render_template("pages/welcome.jinja")


#-----------------------------------------------------------
# Creature list page - Show all the creatures
#-----------------------------------------------------------
@app.get("/creatures")
def show_all_creatures():
    with connect_db() as db:
        sql = """
            SELECT id, species, name, image_file
            FROM creatures
        """
        params = ()
        creatures = db.execute(sql, params).fetchall()

        return render_template("pages/creature_list.jinja", creatures=creatures)


#-----------------------------------------------------------
# Help page - Show some help
#-----------------------------------------------------------
@app.get("/add_creature")
def show_help():
    return render_template("pages/add_creature.jinja")

@app.post("/add")
def add_creature():
    name = request.form.get('name', '').strip()
    species = request.form.get('species', '').strip()
    image_file = request.files.get('image', None)

    if not image_file or image_file.filename == '':
        flash("There was a problem uploading the image", "error")
        return redirect("/")

    # Sanitise filename and make it unique
    filename = secure_filename(image_file.filename)
    random_prefix = uuid.uuid4().hex[:12]
    unique_filename = f"{random_prefix}_{filename}"

    # Get the path of the upload folder
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

    # Save file to disk
    image_file.save(filepath)
    with connect_db() as db:
        sql = """
            INSERT INTO creatures (name, species, image_file)
            VALUES (?, ?, ?)
        """
        params = (name, species, unique_filename)
        db.execute(sql, params)

    return redirect('/creatures')


@app.get("/remove/<int:id>")
def remove_creature(id):
    with connect_db() as db:
        sql = """
            SELECT name, image_file
            FROM creatures WHERE id = ?
        """
        params = (id,)
        creature = db.execute(sql, params).fetchone()
        
        if creature['name'] == "Just the two of us guy":
            flash("You will not harm our lord.", 'error')
        else:
            filepath = os.path.join(UPLOAD_FOLDER, creature['image_file'])
            if os.path.exists(filepath):
                os.remove(filepath)
            sql = """
                DELETE FROM creatures 
                WHERE id = ?
            """
            params = (id,)
            db.execute(sql, params)

            flash(f"{creature['name']} was taken out back.", 'success')
    return redirect('/creatures')





#===========================================================
# Configure the app
#===========================================================
load_dotenv()
app.config.from_prefixed_env()
init_logging(app)
init_text_filters(app)
init_date_filters(app)
init_error_handlers(app)
init_database()
register_commands(app)

