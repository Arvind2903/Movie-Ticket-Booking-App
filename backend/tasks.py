import datetime
from .workers import celery
from celery.schedules import crontab
from . import models
from flask import current_app as app
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64
import os
import matplotlib.pyplot as plt
from jinja2 import Template
from weasyprint import HTML
import pandas as pd

host = app.config['SMTP_SERVER_HOST']
port = app.config['SMTP_SERVER_PORT']
sender_address = app.config['SENDER_ADDRESS']
sender_password = app.config['SENDER_PASSWORD']
mainDirectory = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
graphSaveDirectory = os.path.join(mainDirectory, 'frontend', "src", "assets", "graphs")
if not os.path.exists(graphSaveDirectory):
    os.makedirs(graphSaveDirectory)
THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__)) + os.sep
base_url = 'file://' + THIS_FILE_DIR

# Function to check if the user has logged in that day
def loginCheck(user):
    today_day = datetime.datetime.now().day
    logins = models.Activity.query.filter_by(user_id=user.id).filter_by(activity='login').all()
    for activity in logins:
        if activity.timestamp.day == today_day:
            return True
    return False

# Function to check if the user has posted that day
def bookingsCheck(user):
    today_day = datetime.datetime.now().day
    bookings = models.Activity.query.filter_by(user_id=user.id).filter_by(activity='booked tickets').all()
    for activity in bookings:
        if activity.timestamp.day == today_day:
            return True
    return False

# General function to email MailHog
def sendEmail(to_address, subject, message, attachments=None):
    msg = MIMEMultipart()
    msg["From"] = sender_address
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "html"))

    if attachments:
        for attachment in attachments:
            if attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(open(attachment, "rb").read())
                part.add_header(
                    "Content-Disposition", f"attachment; filename= {os.path.basename(attachment)}"
                )
                encode_base64(part)
                msg.attach(part)

    s = smtplib.SMTP(host=host, port=port)
    s.login(sender_address, sender_password)
    s.send_message(msg)
    s.quit()


# Send reminder if not logged/booked
@celery.task()
def sendReminders():
    users = models.User.query.all()
    recipients = []
    for user in users:
        if not loginCheck(user):
            with open(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'templates',
                                   'LoginReminderTemplate.html')) as file_:
                template = Template(file_.read())
                message = template.render(user=user)
            recipients.append({"name": user.name, "email": user.email, "subject": "Login Reminder",
                               "message": message})
        elif loginCheck(user) and not bookingsCheck(user):
            with open(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'templates',
                                   'BookingReminderTemplate.html')) as file_:
                template = Template(file_.read())
                message = template.render(user=user)
            recipients.append({"name": user.name, "email": user.email, "subject": "Booking Reminder",
                               "message": message})

    for user in recipients:
        sendEmail(to_address=user["email"], subject=user["subject"], message=user["message"])


# Send monthly reports
@celery.task()
def sendReports():
    users = models.User.query.all()
    now = datetime.datetime.now()
    month = now.strftime("%B")
    oneMonthBack = now - datetime.timedelta(days=30)
    twoMonthsBack =  now - datetime.timedelta(days=60)
    activities = ["login", "booked tickets"]
    current_month_logins = 0
    previous_month_logins = 0
    for user in users:
        bar1, bar2 = [], []
        for activity in activities:
            oneMonth = len([item.timestamp for item in models.db.session.query(models.Activity).filter_by(user_id=user.id).
                        filter_by(activity=activity).filter(models.Activity.timestamp>oneMonthBack).all()])
            twoMonths = len([item.timestamp for item in models.db.session.query(models.Activity).filter_by(user_id=user.id).
                        filter_by(activity=activity).filter(models.Activity.timestamp > twoMonthsBack).
                        filter(models.Activity.timestamp<=oneMonthBack).all()])
            if activity=="login":
                current_month_logins = oneMonth
                previous_month_logins = twoMonths
            bar1.append(oneMonth)
            bar2.append(twoMonths)
        data = {'Last Month':bar1, 'Month Before':bar2}
        df = pd.DataFrame(data, index=activities)
        plt.figure(figsize=(4, 6))
        ax = df.plot(kind='bar', rot=0, xlabel="Activity", ylabel="",
                     title='Engagement Graph for {user}'.format(user=user.name))
        for c in ax.containers:
            ax.bar_label(c, label_type='edge',
                         labels=[str(count) if count != 0 else "" for count in c.datavalues])
        plt.legend(loc='best')
        plt.tight_layout()
        plt.savefig(os.path.join(graphSaveDirectory, "{user}.png".format(user=user.name)))
        plt.switch_backend('agg')

        if user.admin:
            adminActivities = ['added theatre', 'added movie']
            adminBar1, adminBar2 = [], []
            for adminActivity in adminActivities:
                oneMonth = len([item.timestamp for item in models.db.session.query(models.Activity).filter_by(user_id=user.id).
                    filter_by(activity=adminActivity).filter(models.Activity.timestamp > oneMonthBack).all()])
                twoMonths = len([item.timestamp for item in models.db.session.query(models.Activity).filter_by(user_id=user.id).
                    filter_by(activity=adminActivity).filter(models.Activity.timestamp > twoMonthsBack).
                    filter(models.Activity.timestamp <= oneMonthBack).all()])
                adminBar1.append(oneMonth)
                adminBar2.append(twoMonths)
            adminData = {'Last Month': adminBar1, 'Month Before': adminBar2}
            adminDf = pd.DataFrame(adminData, index=adminActivities)
            plt.figure(figsize=(4, 6))
            ax = adminDf.plot(kind='bar', rot=0, xlabel="Admin Activity", ylabel="",
                         title='Admin Engagement Graph for {user}'.format(user=user.name))
            for c in ax.containers:
                ax.bar_label(c, label_type='edge',
                             labels=[str(count) if count != 0 else "" for count in c.datavalues])
            plt.legend(loc='best')
            plt.tight_layout()
            plt.savefig(os.path.join(graphSaveDirectory, "{user}_admin.png".format(user=user.name)))
            plt.switch_backend('agg')

        tickets = models.db.session.query(models.Ticket).filter_by(user_id=user.id).filter(
            models.Ticket.timestamp>oneMonthBack).all()
        nTickets = sum([ticket.number_of_tickets for ticket in tickets])

        theatres = list(set([models.Theatre.query.get(ticket.theatre_id).id for ticket in tickets]))
        movies = list(set([models.Movie.query.get(ticket.movie_id).id for ticket in tickets]))
        genres = list(set([models.Movie.query.get(ticket.movie_id).genre for ticket in tickets]))
        languages = list(set([models.Movie.query.get(ticket.movie_id).language for ticket in tickets]))
        theatreBookings = {models.Theatre.query.get(theatre).name: sum([ticket.number_of_tickets for ticket in tickets if
                                         ticket.theatre_id == theatre]) for theatre in theatres}
        movieBookings = {models.Movie.query.get(movie).name: sum([ticket.number_of_tickets for ticket in tickets if
                                     ticket.movie_id == movie]) for movie in movies}
        genreBookings = {genre: sum([ticket.number_of_tickets for ticket in tickets if
                                     models.Movie.query.get(ticket.movie_id).genre == genre]) for genre in genres}
        languageBookings = {language: sum([ticket.number_of_tickets for ticket in tickets if
                                           models.Movie.query.get(ticket.movie_id).language == language]) for language in languages}

        def dictToPie(filename, name, D):
            values = D.values()
            labels = D.keys()
            fig,Ax = plt.subplots()
            Ax.pie(values, labels=labels, pctdistance=0.5, labeldistance=0.2, startangle=10,
                    autopct=lambda x: f'{x:.1f}%')
            plt.axis('equal')
            Ax.set_title('Ticket Bookings by {category}'.format(category=name))
            plt.savefig(os.path.join(graphSaveDirectory, "{name}.png".format(name=filename)))
        for key,d in zip(['theatres','movies','genres','languages'],
                         [theatreBookings,movieBookings,genreBookings,languageBookings]):
            dictToPie(key+'_'+user.name, key, d)

        with open(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'templates',
                               'ReportTemplate.html')) as file_:
            template = Template(file_.read())
            message = template.render(user=user, current_month_logins=current_month_logins, n=nTickets,
                                      previous_month_logins=previous_month_logins, month=month)
            html = HTML(string=message, base_url=base_url)
            file_name = os.path.join(mainDirectory, 'frontend', 'src', 'assets', 'pdfs', "{name}.pdf".format(name=user.name))
            html.write_pdf(target=file_name)
        with open(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'templates',
                               'ReportMessageTemplate.html')) as file_:
            template = Template(file_.read())
            message = template.render(user=user, month=month)
            sendEmail(to_address=user.email, subject="Monthly Engagement Report",
                  message=message, attachments=[os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src','assets',
                                                           'pdfs', '{name}.pdf'.format(name=user.name))])



@celery.task
def generateCSV(theatre_id, user_id):
    theatre = models.Theatre.query.get(theatre_id)
    user = models.User.query.get(user_id)
    theatre_data = {
        'Name': theatre.name,
        'Address': theatre.address,
        'Wheelchair Facilities': "Available" if (theatre.wheelchair==1) else "Not Available",
        'Wheelchair Parking': "Available" if (theatre.parking == 1) else "Not Available",
        'Wheelchair Food & Beverage': "Available" if (theatre.fnb == 1) else "Not Available",
        'Maximum Number of Shows per Movie': theatre.max_shows,
        'Total Number of Seats per Screen': theatre.total_seats,
    }
    movie_ids = list(set([schedule.movie_id for schedule in models.MovieSchedule.query.filter_by(theatre_id=theatre_id)]))
    movies = [models.Movie.query.get(movie_id) for movie_id in movie_ids]
    max_price = max(list(set([movie.price for movie in movies])))
    max_price_movie = [movie.name for movie in movies if movie.price==max_price][0]
    max_rating = max(list(set([movie.rating for movie in movies])))
    max_rating_movie = [movie.name for movie in movies if movie.rating == max_rating][0]
    max_runtime = max(list(set([movie.runtime for movie in movies])))
    max_runtime_movie = [movie.name for movie in movies if movie.runtime == max_runtime][0]
    movie_data = {
        'Movies Show': list(set([movie.name for movie in movies])),
        'Genres Shown': list(set([movie.genre for movie in movies])),
        'Languages Shown': list(set([movie.language for movie in movies])),
        'Subtitles Supported': list(set([movie.subtitles for movie in movies])),
        'Costliest Movie': f"{max_price_movie}: {max_price}",
        'Highest Rated Movie': f"{max_rating_movie}: {max_rating}",
        'Longest Running Film': f"{max_runtime_movie}: {max_runtime}"
    }
    df_theatre = pd.DataFrame([theatre_data])
    df_movies = pd.DataFrame([movie_data])
    file_name_user = os.path.join(mainDirectory, 'frontend', 'src', 'assets', 'csvs',
                                  "{name}.csv".format(name=theatre.name))
    file_name_post = os.path.join(mainDirectory, 'frontend', 'src', 'assets', 'csvs',
                                  "{name}_movies.csv".format(name=theatre.name))
    df_theatre.to_csv(file_name_user, index=False)
    df_movies.to_csv(file_name_post, index=False)
    with open(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'templates',
                           'CSVMessageTemplate.html')) as file_:
        template = Template(file_.read())
        message = template.render(user=user, theatre=theatre.name)
    sendEmail(to_address=user.email, subject="Theatre Dashboard",
              message=message, attachments=[os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'assets',
                                                         'csvs', '{name}.csv'.format(name=theatre.name)),
                                            os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'assets',
                                                         'csvs', '{name}_movies.csv'.format(name=theatre.name))
                                            ])


@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):

    # Every morning at 10 AM
    sender.add_periodic_task(crontab(),
                             sendReminders.s(),
                             name="daily reminders")

    # Every month beginning
    sender.add_periodic_task(crontab(),
                             sendReports.s(),
                             name="monthly reports")

