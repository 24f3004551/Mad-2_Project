from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hospital.db"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
db = SQLAlchemy(app)


# ----------------------Models----------------------------------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    blacklist = db.Column(db.Boolean, default=False)
    department_id = db.Column(
        db.Integer(),
        db.ForeignKey("departments.id"),
        nullable=True,
    )
    created_at = db.Column(db.DateTime, default=datetime.now())

    department = db.relationship("Department", back_populates="doctors")
    appointments_as_patient = db.relationship(
        "Appointment",
        foreign_keys="Appointment.patient_id",
        back_populates="patient",
        cascade="all, delete",
        order_by="Appointment.date",
    )

    appointments_as_doctor = db.relationship(
        "Appointment",
        foreign_keys="Appointment.doctor_id",
        back_populates="doctor",
        order_by="Appointment.date",
    )
    available_slots = db.relationship(
        "DoctorAvailability", back_populates="doctor", cascade="all, delete-orphan"
    )


class DoctorAvailability(db.Model):
    __tablename__ = "doctor_availability"
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    slot = db.Column(db.String(20), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    is_booked = db.Column(db.Boolean, default=False)

    doctor = db.relationship("User", back_populates="available_slots")


class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    doctors = db.relationship("User", back_populates="department")


class Appointment(db.Model):
    __tablename__ = "appointment"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    slot = db.Column(db.String(20), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    status = db.Column(db.String(20), default="Booked", nullable=False)

    treatment = db.relationship(
        "Treatment",
        back_populates="appointment",
        uselist=False,
        cascade="all, delete-orphan",
    )
    patient = db.relationship(
        "User", foreign_keys=[patient_id], back_populates="appointments_as_patient"
    )
    doctor = db.relationship(
        "User", foreign_keys=[doctor_id], back_populates="appointments_as_doctor"
    )


class Treatment(db.Model):
    __tablename__ = "treatment"
    id = db.Column(db.Integer(), primary_key=True)
    appointment_id = db.Column(
        db.Integer(), db.ForeignKey("appointment.id"), unique=True
    )
    diagnosis = db.Column(db.String(500), nullable=False)
    prescription = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.String(500), nullable=True)

    appointment = db.relationship("Appointment", back_populates="treatment")


# ---------------------Routes-----------------------------------
@app.route("/")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    role = session.get("role")

    if role == "admin":
        return redirect("/admin_dashboard")
    elif role == "patient":
        return redirect(url_for("patient_dashboard"))
    elif role == "doctor":
        return redirect("/doctor_dashboard")
    else:
        session.clear()
        return redirect("/login")


# --------------------Admin Routes-------------------------------------------
@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/")
    if request.method == "GET":
        doctors = User.query.filter_by(role="doctor").all()
        patients = User.query.filter_by(role="patient").all()
        departments = Department.query.all()
        appointments = Appointment.query.all()
        return render_template(
            "admin_dashboard.html",
            doctors=doctors,
            patients=patients,
            departments=departments,
            appointments=appointments,
        )


@app.route("/admin_doctors", methods=["GET"])
def admin_doctors():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/")
    if request.method == "GET":
        search_term = request.args.get("q", "").strip()
        if search_term:
            doctors = User.query.filter_by(role="doctor")

            doctors = doctors.join(Department)

            doctors = doctors.filter(
                (User.username.like(f"%{search_term}%"))
                | (Department.name.like(f"%{search_term}%"))
            ).all()

        else:
            doctors = User.query.filter_by(role="doctor").all()
        departments = Department.query.all()
        global_doctors = User.query.filter_by(role="doctor").all()
        return render_template(
            "admin_doctors.html",
            doctors=doctors,
            departments=departments,
            global_doctors=global_doctors,
        )


@app.route("/admin/add_doctor", methods=["POST"])
def add_doctor():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/")
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    dept = request.form.get("selected_dept", "")

    if username == "" or password == "":
        flash("Please provide username and password", "error")
        return redirect("/admin_doctors")

    doctorExist = User.query.filter_by(username=username).first()

    if doctorExist:
        flash("A user with this username already exist.", "error")
        return redirect("/admin_doctors")

    if dept == "":
        new_doctor = User(
            username=username, password=generate_password_hash(password), role="doctor"
        )
    else:
        new_doctor = User(
            username=username,
            password=generate_password_hash(password),
            role="doctor",
            department_id=int(dept),
        )
    db.session.add(new_doctor)
    db.session.commit()
    flash(f"Created new doctor {new_doctor.username}", "success")
    return redirect("/admin_doctors")


@app.route("/admin/update_doctor/<int:user_id>", methods=["GET", "POST"])
def update_doctor(user_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/")

    doctor = User.query.filter_by(id=user_id, role="doctor").first()

    if not (doctor):
        flash("Cannot find doctor", "error")
        return redirect(f"/admin/update_doctor/{user_id}")

    if request.method == "GET":
        departments = Department.query.all()
        return render_template(
            "update_doctor.html", doctor=doctor, departments=departments
        )

    new_username = request.form.get("username").strip()
    new_department_id = request.form.get("department_id")

    doctor.username = new_username
    doctor.department_id = (
        int(new_department_id)
        if new_department_id and new_department_id != "None"
        else None
    )

    db.session.commit()
    flash(f"Doctor {doctor.username} updated successfully.")
    return redirect(url_for("admin_doctors"))


@app.route("/admin/blacklist_user/<int:user_id>/<string:username>", methods=["POST"])
def blacklist_user(user_id, username):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/")
    user = User.query.filter_by(username=username, id=user_id).first()

    if not (user):
        flash("This user does not exist", "error")
        return redirect("/admin_dashboard")

    user.blacklist = not user.blacklist
    db.session.commit()

    if user.blacklist:
        flash(f"{username} has been blacklisted.", "success")
    else:
        flash(f"Blacklist removed {username}.", "success")

    if user.role == "doctor":
        return redirect("/admin_doctors")
    else:
        return redirect("/admin_patients")


@app.route("/admin/delete_doctor/<int:user_id>", methods=["POST"])
def delete_doctor(user_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/")

    doctor = User.query.filter_by(id=user_id, role="doctor").first()

    if not doctor:
        flash("Doctor not found.", "error")
        return redirect("/admin_doctors")

    today = datetime.now().date()
    upcoming = Appointment.query.filter(
        Appointment.doctor_id == doctor.id, Appointment.date >= today
    ).all()
    past = Appointment.query.filter(
        Appointment.doctor_id == doctor.id, Appointment.date < today
    ).all()

    for appt in upcoming:
        appt.doctor_id = None
        if appt.status == "Booked":
            appt.status = "Cancelled"

    for appt in past:
        appt.doctor_id = None

    db.session.delete(doctor)
    db.session.commit()

    flash(
        f"Doctor {doctor.username} deleted",
        "success",
    )
    return redirect("/admin_doctors")


@app.route("/admin_patients")
def admin_patients():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/")

    search_term = request.args.get("q", "").strip()
    if search_term:
        patients = User.query.filter(
            User.role == "patient", User.username.like(f"%{search_term}%")
        ).all()
    else:
        patients = User.query.filter_by(role="patient").all()
    global_patients = User.query.filter_by(role="patient").all()
    return render_template(
        "admin_patients.html", patients=patients, global_patients=global_patients
    )


@app.route("/admin/delete_patient/<int:user_id>", methods=["POST"])
def delete_patient(user_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/")

    patient = User.query.filter_by(id=user_id, role="patient").first()
    if not patient:
        flash("Patient not found.", "error")
        return redirect("/admin_patients")

    today = datetime.now().date()
    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient.id, Appointment.date >= today
    ).all()
    for appt in upcoming:
        slot = DoctorAvailability.query.filter_by(
            slot=appt.slot, doctor_id=appt.doctor_id, date=appt.date
        ).first()
        if slot and slot.is_booked:
            slot.is_booked = False

    db.session.delete(patient)
    db.session.commit()

    flash(
        f"Patient {patient.username} deleted",
        "success",
    )
    return redirect("/admin_patients")


@app.route("/admin_departments")
def admin_departments():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/")

    departments = Department.query.all()
    doctors_with_no_dept = User.query.filter_by(
        role="doctor", department_id=None, blacklist=False
    ).all()
    return render_template(
        "admin_departments.html",
        departments=departments,
        doctors_with_no_dept=doctors_with_no_dept,
    )


@app.route("/admin/add_department", methods=["POST"])
def add_department():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/")
    dept_name = request.form.get("dept_name", "")
    desc = request.form.get("description", "")
    selected_doctor_ids = request.form.getlist("doctor_ids")

    if dept_name == "":
        flash(f"Please provide a department name", "error")
        return redirect("/admin_departments")

    dept_exist = Department.query.filter_by(name=dept_name).first()

    if dept_exist:
        return "A department with this name already exists", 400

    new_dept = Department(name=dept_name, description=desc)
    db.session.add(new_dept)
    db.session.commit()

    if selected_doctor_ids:
        for doc_id in selected_doctor_ids:
            doctor = User.query.filter_by(id=int(doc_id)).first()
            if doctor and doctor.role == "doctor":
                doctor.department_id = new_dept.id
        db.session.commit()

    flash(f"Department '{dept_name}' created successfully!")
    return redirect("/admin_departments")


@app.route("/admin/update_department/<int:dept_id>", methods=["GET", "POST"])
def update_department(dept_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/")

    dept = Department.query.filter_by(id=dept_id).first()

    if not dept:
        flash("Could not find Department", "error")
        return redirect("/admin_departments")

    if request.method == "GET":
        return render_template("update_department.html", dept=dept)

    dept_name = request.form.get("name", "")
    dept_description = request.form.get("description", "")

    if dept_name == "":
        flash("Please provide a department name", "error")
        return redirect(f"/admin/update_department/{dept_id}")

    dept.name = dept_name
    dept.description = dept_description

    db.session.commit()
    flash("Department updated successfully!")
    return redirect(url_for("admin_departments"))


@app.route("/admin/delete_department/<int:dept_id>", methods=["POST"])
def delete_department(dept_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/")

    dept = Department.query.filter_by(id=dept_id).first()

    if not dept:
        flash("Could not find department", "error")
        return redirect("/admin_departments")

    for doctor in dept.doctors:
        doctor.department_id = None

    db.session.delete(dept)
    db.session.commit()

    flash("Deleted Department Successfully", "success")
    return redirect("/admin_departments")


@app.route("/admin_appointments")
def admin_appointments():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/")

    appointments = Appointment.query.all()
    patients = User.query.filter_by(role="patient").all()
    doctors = User.query.filter_by(role="doctor").all()
    today = datetime.today().isoformat()
    return render_template(
        "admin_appointments.html",
        appointments=appointments,
        doctors=doctors,
        patients=patients,
        today=today,
    )


@app.route("/admin/delete_appointment/<int:appt_id>", methods=["POST"])
def delete_appointment(appt_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/")
    appt = Appointment.query.filter_by(id=appt_id).first()

    if not appt:
        flash("Could not find appointment", "error")
        return redirect("/admin_appointments")

    slot = DoctorAvailability.query.filter_by(
        doctor_id=appt.doctor_id, date=appt.date, slot=appt.slot
    ).first()
    if slot:
        slot.is_booked = False

    db.session.delete(appt)
    db.session.commit()
    flash("Appointment deleted successfully.", "success")
    return redirect("/admin_appointments")


# ---------------------Doctor Routes-----------------------------------------
@app.route("/doctor_dashboard", methods=["GET", "POST"])
def doctor_dashboard():
    if "user_id" not in session or session["role"] != "doctor":
        return redirect("/")

    if request.method == "GET":
        username = session["username"]
        today = datetime.now().date()
        doctor = User.query.filter_by(username=username).first()

        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status.in_(["Booked", "Finished"]),
        ).all()

        patient_ids = []

        for appt in appointments:
            if appt.patient_id not in patient_ids:
                patient_ids.append(appt.patient_id)

        assigned_patients = User.query.filter(User.id.in_(patient_ids)).all()

        daily_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.date == today,
            Appointment.status == "Booked",
        ).all()
        return render_template(
            "doctor_dashboard.html",
            doctor=doctor,
            daily_appointments=daily_appointments,
            assigned_patients=assigned_patients,
        )


@app.route("/doctor_availability", methods=["GET", "POST"])
def doctor_availability():

    if "user_id" not in session or session["role"] != "doctor":
        return redirect("/")

    today = datetime.now().date()
    curr_time = datetime.now().time()
    user_id = int(session["user_id"])

    if request.method == "GET":
        upcoming_days = []
        for i in range(7):
            upcoming_days.append(today + timedelta(days=i))

        records = DoctorAvailability.query.filter_by(doctor_id=user_id).all()
        doctor = User.query.filter_by(id=user_id).first()

        if not doctor:
            flash("Error getting doctor", "error")
            return redirect("/doctor_dashboard")

        avail = {}
        for r in records:
            avail[(r.date, r.slot)] = {
                "available": r.is_available,
                "booked": r.is_booked,
            }

        TIME_SLOTS = {
            "slot1": "08:00 AM - 09:00 AM",
            "slot2": "09:00 AM - 10:00 AM",
            "slot3": "10:00 AM - 11:00 PM",
            "slot4": "01:00 PM - 02:00 PM",
            "slot5": "02:00 PM - 03:00 PM",
            "slot6": "03:00 PM - 04:00 PM",
        }

        return render_template(
            "doctor_slots.html",
            days=upcoming_days,
            avail=avail,
            slots=TIME_SLOTS,
            curr_time=curr_time,
            today=today,
            doctor=doctor,
            time=time,
        )

    if request.method == "POST":
        TIME_SLOTS = ["slot1", "slot2", "slot3", "slot4", "slot5", "slot6"]

        for i in range(7):
            day = today + timedelta(days=i)

            for slot in TIME_SLOTS:
                checkbox_name = f"slot_{day}_{slot}"
                is_checked = True if request.form.get(checkbox_name) else False

                existing = DoctorAvailability.query.filter_by(
                    doctor_id=user_id, date=day, slot=slot
                ).first()

                if existing:
                    existing.is_available = is_checked

                    if not is_checked:
                        appt = Appointment.query.filter_by(
                            doctor_id=user_id,
                            date=day,
                            slot=slot,
                            status="Booked",
                        ).first()

                        if appt and appt.status == "Booked":
                            appt.status = "Cancelled"

                        existing.is_booked = False

                else:
                    new_slot = DoctorAvailability(
                        doctor_id=user_id,
                        date=day,
                        slot=slot,
                        is_available=is_checked,
                    )
                    db.session.add(new_slot)

        db.session.commit()
        flash("Updated Doctor Availability", "success")
        return redirect(request.path)


@app.route("/give_treatment/<int:appt_id>", methods=["GET", "POST"])
def give_treatment(appt_id):
    if "user_id" not in session or session["role"] != "doctor":
        return redirect("/")

    appt = Appointment.query.filter_by(id=appt_id).first()
    if not appt:
        flash("Appointment not found", "error")
        return redirect(url_for("doctor_dashboard"))
    past_history = Appointment.query.filter(
        Appointment.id != appt_id,
        Appointment.doctor_id == appt.doctor_id,
        Appointment.patient_id == appt.patient_id,
        Appointment.status == "Finished",
    ).all()

    if request.method == "GET":
        return render_template(
            "treatment.html", appt=appt, past_history=past_history, doctor=appt.doctor
        )

    if request.method == "POST":
        diagnosis = request.form.get("diagnosis")
        prescription = request.form.get("prescription")
        notes = request.form.get("notes")

        if not diagnosis:
            flash("Please provide a diagnosis", "error")
            return redirect(request.path)

        existing = Treatment.query.filter_by(appointment_id=appt_id).first()
        if existing:
            existing.diagnosis = diagnosis
            existing.notes = notes
            existing.prescription = prescription
        else:
            new_treatment = Treatment(
                diagnosis=diagnosis,
                notes=notes,
                prescription=prescription,
                appointment_id=appt_id,
            )
            db.session.add(new_treatment)

        appt.status = "Finished"

        availability = DoctorAvailability.query.filter_by(
            doctor_id=appt.doctor_id, date=appt.date, slot=appt.slot
        ).first()
        if availability:
            availability.is_booked = False
            availability.is_available = True
        db.session.commit()
        flash("Treatment done!!", "success")
        return redirect(url_for("doctor_dashboard"))


# ---------------------Patient Routes----------------------------------------
@app.route("/patient_dashboard", methods=["GET", "POST"])
def patient_dashboard():
    if "user_id" not in session or session["role"] != "patient":
        return redirect("/")

    if request.method == "GET":

        username = session["username"]
        user_id = int(session["user_id"])
        user = User.query.filter_by(id=user_id, username=username).first()
        doctors = User.query.filter_by(role="doctor").all()
        active_doctors = User.query.filter_by(role="doctor", blacklist=False).all()
        today = datetime.now().date()
        daily_appointments = Appointment.query.filter(
            Appointment.patient_id == user.id,
            Appointment.date == today,
            Appointment.status == "Booked",
        ).all()
        search_term = request.args.get("q", "").strip()
        if search_term:
            doctors = User.query.filter_by(role="doctor")

            doctors = doctors.join(Department)

            doctors = doctors.filter(
                (User.username.like(f"%{search_term}%"))
                | (Department.name.like(f"%{search_term}%"))
            ).all()
        return render_template(
            "patient_dashboard.html",
            user=user,
            doctors=doctors,
            active_doctors=active_doctors,
            daily_appointments=daily_appointments,
        )


@app.route(
    "/setup_appointment/<int:patient_id>/<int:doctor_id>", methods=["GET", "POST"]
)
def setup_appointment(patient_id, doctor_id):
    if "user_id" not in session:
        return redirect("/")

    patient = User.query.filter_by(id=patient_id, role="patient").first()
    user = User.query.filter_by(id=patient_id, role="patient").first()
    doctor = User.query.filter_by(id=doctor_id, role="doctor").first()

    if not patient or not doctor:
        flash("Error Getting patient or doctor", "error")
        return redirect("/patient_dashboard")

    if request.method == "GET":
        records = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id, is_available=True, is_booked=False
        ).all()
        today = datetime.now().date()
        curr_time = datetime.now().time()
        grouped = {}
        for r in records:
            if r.date not in grouped:
                grouped[r.date] = {}
            grouped[r.date][r.slot] = r.is_available
        print(grouped)

        TIME_SLOTS = {
            "slot1": "08:00 AM - 09:00 AM",
            "slot2": "09:00 AM - 10:00 AM",
            "slot3": "10:00 AM - 11:00 PM",
            "slot4": "01:00 PM - 02:00 PM",
            "slot5": "02:00 PM - 03:00 PM",
            "slot6": "03:00 PM - 04:00 PM",
        }

        return render_template(
            "setup_appointment.html",
            grouped=grouped,
            today=today,
            curr_time=curr_time,
            user=user,
            patient=patient,
            doctor=doctor,
            time=time,
            slots=TIME_SLOTS,
        )

    if request.method == "POST":
        selected = request.form.get("selected_slot")
        if not selected:
            flash("Please select a slot", "error")
            return redirect(request.path)

        date_str, slot = selected.split("|")
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

        other_appt = Appointment.query.filter_by(
            patient_id=patient_id,
            date=date_obj,
            slot=slot,
            status="Booked",
        ).first()
        if other_appt:
            flash("You have another appointment in this slot", "error")
            return redirect(request.path)

        available = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            date=date_obj,
            slot=slot,
            is_available=True,
            is_booked=False,
        ).first()
        if not available:
            flash("The slot is not longer available", "error")
            return redirect(request.path)

        appt = Appointment(
            date=date_obj,
            slot=slot,
            patient_id=patient_id,
            doctor_id=doctor_id,
            status="Booked",
        )
        available.is_booked = True
        db.session.add(appt)
        db.session.commit()

        flash("Appointment booked successfully!", "success")
        return redirect("/patient_dashboard")


@app.route("/view_departments")
def view_departments():
    if "user_id" not in session or session["role"] != "patient":
        return redirect("/")
    user = User.query.filter_by(id=int(session["user_id"])).first()
    if not user:
        flash("Something went wrong", "error")
        return redirect("/")
    departments = Department.query.all()
    return render_template("view_departments.html", departments=departments, user=user)


# ---------------------Auth and Common Routes--------------------------------
@app.route("/view_treatment/<int:appt_id>")
def view_treatment(appt_id):
    if "user_id" not in session or session["role"] == "doctor":
        return redirect("/")

    appt = Appointment.query.filter_by(id=appt_id).first()
    past_history = Appointment.query.filter(
        Appointment.id != appt_id,
        Appointment.doctor_id == appt.doctor_id,
        Appointment.patient_id == appt.patient_id,
        Appointment.status == "Finished",
    ).all()

    if not appt:
        flash("Could not find Appointment", "error")
        return redirect("/")

    if session["role"] == "patient":
        return render_template(
            "view_treatment.html",
            user=appt.patient,
            appt=appt,
            past_history=past_history,
            layout="patient_dashboard.html",
        )

    elif session["role"] == "admin":
        doctors = User.query.filter_by(role="doctor").all()
        patients = User.query.filter_by(role="patient").all()
        departments = Department.query.all()
        appointments = Appointment.query.all()

        return render_template(
            "view_treatment.html",
            appt=appt,
            past_history=past_history,
            doctors=doctors,
            patients=patients,
            departments=departments,
            appointments=appointments,
            layout="admin_dashboard.html",
        )

    else:
        flash("Unauthorized access", "error")
        return redirect("/")


@app.route("/cancel_appointment/<int:appt_id>", methods=["POST"])
def cancel_appointment(appt_id):
    if "user_id" not in session:
        return redirect("/")
    appt = Appointment.query.filter_by(id=appt_id, status="Booked").first()
    if not appt:
        flash("Could not find Appointment", "error")
        return redirect("/")
    slot = DoctorAvailability.query.filter_by(
        date=appt.date,
        slot=appt.slot,
        doctor_id=appt.doctor_id,
        is_booked=True,
    ).first()

    if slot:
        slot.is_booked = False
    appt.status = "Cancelled"
    flash("Cancelled Appointment", "success")
    db.session.commit()
    return redirect("/")


@app.route("/view_profile/<int:user_id>", methods=["GET", "POST"])
def view_profile(user_id):
    if "user_id" not in session:
        return redirect("/")

    user = User.query.filter_by(id=user_id).first()
    if not user:
        flash("User not found", "error")
        return redirect("/")

    if request.method == "GET":
        return render_template("profile.html", user=user)

    if request.method == "POST":
        new_username = request.form.get("username")
        new_password = request.form.get("password")

        changed = False

        if new_username and new_username != user.username:
            user_exists = User.query.filter_by(username=new_username).first()
            if user_exists:
                flash("Username already exists", "error")
                return redirect(request.path)
            user.username = new_username
            session["username"] = new_username
            changed = True

        if new_password and not check_password_hash(user.password, new_password):
            user.password = generate_password_hash(new_password)
            changed = True

        if changed:
            db.session.commit()
            flash("Profile updated successfully!", "success")
        else:
            flash("No changes made", "info")
        return redirect(request.path)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        if "user_id" in session:
            return redirect("/")
        else:
            return render_template("auth.html", auth="signup")
    elif request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == "" or password == "":
            flash("Please provide username and password", "error")
            return redirect(request.path)

        userExist = User.query.filter_by(username=username).first()

        if userExist:
            flash("User with this username already exists", "error")
            return redirect(request.path)

        newUser = User(
            username=username.strip(),
            password=generate_password_hash(password.strip()),
            role="patient",
        )
        db.session.add(newUser)
        db.session.commit()

        session["user_id"] = newUser.id
        session["username"] = newUser.username
        session["role"] = newUser.role

        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "user_id" in session:
            return redirect("/")
        else:
            return render_template("auth.html", auth="login")
    elif request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if user.blacklist:
                flash("User has been blacklisted", "error")
                return redirect("/")

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            return redirect("/")
        else:
            flash("Invalid credentials", "error")
            return redirect(request.path)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        existing_admin = User.query.filter_by(username="admin", role="admin").first()

        if not existing_admin:
            admin_db = User(
                username="admin", password=generate_password_hash("admin"), role="admin"
            )
            db.session.add(admin_db)
            db.session.commit()

    app.run(debug=True)
