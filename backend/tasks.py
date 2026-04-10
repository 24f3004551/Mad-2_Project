from celery_worker import celery_app
from datetime import datetime
import pytz
import csv
from app import db, User, Appointment
from flask import render_template

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

SERVER_SMTP_HOST = "localhost"
SERVER_SMTP_PORT = 1025
SENDER_ADDRESS = "aadishhabeeb123@mail.com"


def send_email(to_address, subject, message, content="text", attachment=None):
    msg = MIMEMultipart()
    msg["To"] = to_address
    msg["From"] = SENDER_ADDRESS
    msg["Subject"] = subject

    if content == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))

    if attachment:
        with open(attachment, "rb") as a:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(a.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={attachment}")
        msg.attach(part)

    s = smtplib.SMTP(host=SERVER_SMTP_HOST, port=SERVER_SMTP_PORT)
    s.send_message(msg)
    s.quit()

    return True


@celery_app.task
def daily_reminders():
    ist = pytz.timezone("Asia/Kolkata")
    today = datetime.now(ist).date()

    appointments = Appointment.query.filter_by(date=today, status="Booked").all()

    for appt in appointments:
        patient = User.query.get(appt.patient_id)

        subject = "Hospital Visit Reminder"

        html_message = render_template(
            "daily_reminder.html", username=patient.username, slot=appt.slot
        )

        send_email(
            f"{patient.username}@mail.com", subject, html_message, content="html"
        )

    return "Daily reminders sent"


@celery_app.task
def monthly_reports():
    from datetime import datetime

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    month = now.month
    year = now.year

    doctors = User.query.filter_by(role="doctor").all()

    for doc in doctors:
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            db.extract("month", Appointment.date) == month,
            db.extract("year", Appointment.date) == year,
        ).all()

        html_content = f"""
        <h2>Monthly Report for Dr. {doc.username}</h2>
        <p>Total Appointments: {len(appointments)}</p>
        <ul>
        """

        for appt in appointments:
            diagnosis = appt.treatment.diagnosis if appt.treatment else "None"
            prescription = appt.treatment.prescription if appt.treatment else "None"
            notes = appt.treatment.notes if appt.treatment else "None"
            html_content += f"""
            <li>
                Date: {appt.date} |
                Patient: {appt.patient.username} |
                Diagnosis: {diagnosis}
                Prescription : {prescription}
                Notes : {notes}
            </li>
            """

        html_content += "</ul>"

        send_email(
            f"{doc.username}@mail.com",
            "Monthly Activity Report",
            html_content,
            content="html",
        )

    return "Monthly reports sent"


@celery_app.task
def export_csv(user_id):
    user = User.query.get(user_id)

    appointments = Appointment.query.filter_by(patient_id=user_id).all()

    filename = f"report_{user_id}.csv"

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(
            ["User ID", "Username", "Doctor", "Date", "Diagnosis", "Treatment", "Notes"]
        )

        for appt in appointments:
            writer.writerow(
                [
                    user.id,
                    user.username,
                    appt.doctor.username if appt.doctor else "None",
                    appt.date,
                    appt.treatment.diagnosis if appt.treatment else "None",
                    appt.treatment.prescription if appt.treatment else "None",
                    appt.treatment.notes if appt.treatment else "None",
                ]
            )

    send_email(
        f"{user.username}@mail.com",
        "Your Treatment Report",
        "Attached is your CSV report",
        content="text",
        attachment=filename,
    )

    return "CSV exported"
