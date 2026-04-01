from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for,
    jsonify,
)
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
    get_jwt,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, time
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__, template_folder="templates")
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hospital.db"
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["JWT_SECRET_KEY"] = "mypersonaljwtsecretkeyformyhospitalapplication"
jwt = JWTManager(app)
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
# @app.route("/")
# def dashboard():
#     if "user_id" not in session:
#         return redirect("/login")

#     role = session.get("role")

#     if role == "admin":
#         return redirect("/admin_dashboard")
#     elif role == "patient":
#         return redirect(url_for("patient_dashboard"))
#     elif role == "doctor":
#         return redirect("/doctor_dashboard")
#     else:
#         session.clear()
#         return redirect("/login")


# --------------------Admin Routes-------------------------------------------
@app.route("/admin_dashboard", methods=["GET"])
@jwt_required()
def admin_dashboard():
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    doctors = User.query.filter_by(role="doctor").all()
    patients = User.query.filter_by(role="patient").all()
    departments = Department.query.all()
    appointments = Appointment.query.all()
    return jsonify(
        {
            "doctors": [
                {
                    "id": d.id,
                    "username": d.username,
                    "blacklist": d.blacklist,
                    "department_id": d.department_id,
                }
                for d in doctors
            ],
            "patients": [
                {"id": p.id, "username": p.username, "blacklist": p.blacklist}
                for p in patients
            ],
            "departments": [
                {
                    "id": dept.id,
                    "name": dept.name,
                    "description": dept.description,
                    "doctors": [
                        {"id": doc.id, "username": doc.username} for doc in dept.doctors
                    ],
                }
                for dept in departments
            ],
            "appointments": [
                {
                    "id": a.id,
                    "date": str(a.date),
                    "slot": a.slot,
                    "status": a.status,
                    "patient": (
                        {"id": a.patient.id, "username": a.patient.username}
                        if a.patient
                        else None
                    ),
                    "doctor": (
                        {"id": a.doctor.id, "username": a.doctor.username}
                        if a.doctor
                        else None
                    ),
                }
                for a in appointments
            ],
        }
    )


@app.route("/admin_doctors", methods=["GET"])
@jwt_required()
def admin_doctors():
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    search_term = request.args.get("q", "").strip()

    if search_term:
        doctors = (
            User.query.filter_by(role="doctor")
            .outerjoin(Department)
            .filter(
                (User.username.like(f"%{search_term}%"))
                | (Department.name.like(f"%{search_term}%"))
            )
            .all()
        )
    else:
        doctors = User.query.filter_by(role="doctor").all()

    departments = Department.query.all()

    return jsonify(
        {
            "doctors": [
                {
                    "id": d.id,
                    "username": d.username,
                    "department": d.department.name if d.department else None,
                    "blacklist": d.blacklist,
                }
                for d in doctors
            ],
            "departments": [{"id": dept.id, "name": dept.name} for dept in departments],
        }
    )


@app.route("/admin/add_doctor", methods=["POST"])
@jwt_required()
def add_doctor():
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    dept_id = data.get("department_id")

    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400

    new_doctor = User(
        username=username,
        password=generate_password_hash(password),
        role="doctor",
        department_id=dept_id if dept_id else None,
    )

    db.session.add(new_doctor)
    db.session.commit()

    return jsonify({"msg": "Doctor created"})


@app.route("/admin/update_doctor/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_doctor(id):
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    doctor = User.query.filter_by(id=id, role="doctor").first()

    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    data = request.get_json()

    doctor.username = data.get("username", doctor.username)
    doctor.department_id = data.get("department_id")

    db.session.commit()

    return jsonify({"msg": "Doctor updated"})


@app.route("/admin/blacklist_user/<int:user_id>", methods=["POST"])
@jwt_required()
def blacklist_user(user_id):
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user.blacklist = not user.blacklist
    db.session.commit()

    return jsonify({"msg": "Updated"})


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


@app.route("/admin_departments", methods=["GET"])
@jwt_required()
def admin_departments():
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    departments = Department.query.all()
    doctors_with_no_dept = User.query.filter_by(
        role="doctor", department_id=None, blacklist=False
    ).all()

    return jsonify(
        {
            "departments": [
                {
                    "id": d.id,
                    "name": d.name,
                    "description": d.description,
                    "doctors": [
                        {"id": doc.id, "username": doc.username} for doc in d.doctors
                    ],
                }
                for d in departments
            ],
            "doctors": [
                {"id": doc.id, "username": doc.username} for doc in doctors_with_no_dept
            ],
        }
    )


@app.route("/admin/add_department", methods=["POST"])
@jwt_required()
def add_department():
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    dept_name = data.get("dept_name", "")
    desc = data.get("description", "")
    selected_doctor_ids = data.get("doctor_ids", [])

    if dept_name == "":
        return jsonify({"error": "Name required"}), 400

    if Department.query.filter_by(name=dept_name).first():
        return jsonify({"error": "Department exists"}), 400

    new_dept = Department(name=dept_name, description=desc)
    db.session.add(new_dept)
    db.session.commit()

    for doc_id in selected_doctor_ids:
        doctor = User.query.get(int(doc_id))
        if doctor and doctor.role == "doctor":
            doctor.department_id = new_dept.id

    db.session.commit()

    return jsonify({"msg": "Created"})


@app.route("/admin/update_department/<int:dept_id>", methods=["POST"])
@jwt_required()
def update_department(dept_id):
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    dept = Department.query.get(dept_id)

    if not dept:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()

    dept.name = data.get("name", dept.name)
    dept.description = data.get("description", dept.description)

    selected_doctor_ids = data.get("doctor_ids", [])

    for doctor in dept.doctors:
        if doctor.id not in selected_doctor_ids:
            doctor.department_id = None

    for doc_id in selected_doctor_ids:
        doctor = User.query.get(doc_id)
        if doctor and doctor.role == "doctor":
            doctor.department_id = dept.id

    db.session.commit()

    return jsonify({"msg": "Updated"})


@app.route("/admin/delete_department/<int:dept_id>", methods=["POST"])
@jwt_required()
def delete_department(dept_id):
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    dept = Department.query.get(dept_id)

    if not dept:
        return jsonify({"error": "Not found"}), 404

    for doctor in dept.doctors:
        doctor.department_id = None

    db.session.delete(dept)
    db.session.commit()

    return jsonify({"msg": "Deleted"})


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
@app.route("/doctor_dashboard", methods=["GET"])
@jwt_required()
def doctor_dashboard():
    claims = get_jwt()

    if claims.get("role") != "doctor":
        return jsonify({"error": "Unauthorized"}), 403

    username = claims.get("username")
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

    return jsonify(
        {
            "doctor": {"id": doctor.id, "username": doctor.username},
            "daily_appointments": [
                {
                    "id": a.id,
                    "date": str(a.date),
                    "slot": a.slot,
                    "status": a.status,
                    "patient": a.patient.username,
                    "has_treatment": True if a.treatment else False,
                }
                for a in daily_appointments
            ],
            "assigned_patients": [
                {"id": p.id, "username": p.username} for p in assigned_patients
            ],
            "all_appointments": [
                {
                    "id": a.id,
                    "date": str(a.date),
                    "slot": a.slot,
                    "status": a.status,
                    "patient": a.patient.username,
                    "has_treatment": True if a.treatment else False,
                }
                for a in doctor.appointments_as_doctor
            ],
        }
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
@app.route("/patient_dashboard", methods=["GET"])
@jwt_required()
def patient_dashboard():
    claims = get_jwt()

    if claims.get("role") != "patient":
        return jsonify({"error": "Unauthorized"}), 403

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    today = datetime.now().date()

    daily_appointments = Appointment.query.filter(
        Appointment.patient_id == user.id,
        Appointment.date == today,
        Appointment.status == "Booked",
    ).all()

    all_appointments = Appointment.query.filter(Appointment.patient_id == user.id).all()

    search_term = request.args.get("q", "").strip()

    doctors_query = User.query.filter_by(role="doctor", blacklist=False)

    if search_term:
        doctors_query = doctors_query.outerjoin(Department).filter(
            (User.username.ilike(f"%{search_term}%"))
            | (Department.name.ilike(f"%{search_term}%"))
        )

    doctors = doctors_query.all()

    return jsonify(
        {
            "daily_appointments": [
                {
                    "id": a.id,
                    "date": a.date.strftime("%Y-%m-%d"),
                    "slot": a.slot,
                    "doctor": a.doctor.username if a.doctor else None,
                    "status": a.status,
                    "has_treatment": bool(a.treatment),
                }
                for a in daily_appointments
            ],
            "all_appointments": [
                {
                    "id": a.id,
                    "date": a.date.strftime("%Y-%m-%d"),
                    "slot": a.slot,
                    "doctor": a.doctor.username if a.doctor else None,
                    "status": a.status,
                    "has_treatment": bool(a.treatment),
                }
                for a in all_appointments
            ],
            "doctors": [
                {
                    "id": d.id,
                    "username": d.username,
                    "department": d.department.name if d.department else "No dept",
                }
                for d in doctors
            ],
        }
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


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    userExist = User.query.filter_by(username=username).first()
    if userExist:
        return jsonify({"error": "User already exists"}), 400

    newUser = User(
        username=username, password=generate_password_hash(password), role="patient"
    )
    db.session.add(newUser)
    db.session.commit()

    token = create_access_token(
        identity=str(newUser.id),
        additional_claims={"role": newUser.role, "username": newUser.username},
    )

    return (
        jsonify(
            {
                "token": token,
                "user": {
                    "id": newUser.id,
                    "username": newUser.username,
                    "role": newUser.role,
                },
            }
        ),
        201,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    if user.blacklist:
        return jsonify({"error": "User is blacklisted"}), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "username": user.username},
    )

    return (
        jsonify(
            {
                "token": token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                },
            }
        ),
        201,
    )


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
