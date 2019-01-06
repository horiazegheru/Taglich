from flask import Flask, render_template, request, session
import os
from models.user import User
from models.job import Job

app = Flask(__name__)
# dictionar care trebuie inlocuit cu db
global_dict = {}

# incrementez la fiecare add ca sa fie diferiti, poate scapam de asta cu db-ul
users_index = 0
jobs_index = 0

# aici trebuie puse la inceput toate
job_types = ["Dadaca", "Instalator", "Electrician", "Gradinar", "Menajera", "Altele"]

@app.route('/')
def index():
    if session.get('logged_in'):
        if session.get('account_type') == 'Client':
            return render_template('/clientHomePage.html', **{'job_types': job_types,
                                                              'username': session.get('username')})
        if session.get('account_type') == 'Worker':
            return worker_home_page()
    else:
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if session.get('logged_in'):
        if session.get('account_type') == 'Client':
            return render_template('/clientHomePage.html', **{'job_types': job_types,
                                                              'username': session.get('username')})
        if session.get('account_type') == 'Worker':
            return worker_home_page()

    email = request.form['email']
    password = request.form['password']

    for user in global_dict['users']: # MIHAI
        if user.email == email and user.password == password:
            # cu session tinem minte userul curent, mi-a fost sila sa caut
            # de ce n-a mers sa atribui user ca obiect

            session['username'] = user.username
            session['account_type'] = user.account_type
            session['job_type'] = user.job_type
            session['logged_in'] = True

            if user.account_type == 'Client':
                return render_template('/clientHomePage.html', **{'job_types': job_types,
                                                                  'username': session.get('username')})

            if user.account_type == 'Worker':
                return worker_home_page()

    return index()

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['username'] = None
    session['account_type'] = None
    session['logged_in'] = False

    return index()

@app.route('/register', methods=['GET', 'POST'])
def register():
    global users_index
    global job_types

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        repassword = request.form['repassword']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        dob = request.form['dob']
        description = request.form['description']
        phone_nr = request.form['phone_nr']
        account_type = request.form['account_type']
        job_type = request.form['job_type']

        user = User(users_index, username, email, password, firstname, lastname, dob,
                    description, phone_nr, account_type, job_type)

        users_index += 1

        if password == repassword:
            global_dict['users'].append(user)
            print_users()
            session['logged_in'] = True
            session['username'] = user.username
            session['account_type'] = user.account_type
            session['job_type'] = user.job_type

            print(session['username'])

            if user.account_type == 'Client':
                return render_template('/clientHomePage.html', **{'job_types': job_types,
                                                                  'username': session.get('username')})

            if user.account_type == 'Worker':
                return worker_home_page()

        else:
            return render_template('/register.html')

    else:
        return render_template('/register.html', **{'job_types': job_types})

# neterminat
@app.route('/changePassword', methods=['POST'])
def change_password():
    email = request.form['email']
    password = request.form['password']
    repassword = request.form['repassword']

# aici se adauga un job nou de catre client
@app.route('/clientHomePage', methods=['GET', 'POST'])
def client_home_page():
    global jobs_index

    job_type = request.form['job_type']
    address = request.form['address']
    description = request.form['description']

    job = Job(jobs_index, job_type, address, description, session.get('username'))
    jobs_index += 1

    global_dict['jobs'].append(job)
    print_jobs()

    return render_template('/clientHomePage.html', **{'job_types': job_types})

# worker vede joburile care sunt pt el (gen plumber) si care nu-s Done
@app.route('/workerHomePage', methods=['GET', 'POST'])
def worker_home_page():
    current_job_type = session['job_type']
    matched_jobs = [job for job in global_dict['jobs'] if job.job_type == current_job_type and
                    job.worker_id is None and not job.done]

    return render_template('/workerHomePage.html', **{'username': session.get('username'),
                                                      'jobs': matched_jobs})

# worker isi asigneaza job
@app.route('/workerRequestJob', methods=['GET', 'POST'])
def assign_job():
    job_id = request.form['list_index']

    for job in global_dict['jobs']:
        if int(job.id) == int(job_id):
            current_user_id = get_current_user_id()
            job.assign_worker(current_user_id)

    return worker_home_page()

@app.route('/workerCancelJob', methods=['POST'])
def cancel_job():
    job_id = request.form['list_index']
    for job in global_dict['jobs']:
        if int(job.id) == int(job_id):
            job.worker_id = None

    return jobs_by_worker()

# client marcheaza job done => apare in history si la el si la worker
@app.route('/clientMarkJobDone', methods=['POST'])
def job_done():
    job_id = request.form['list_index']
    for job in global_dict['jobs']:
        if int(job.id) == int(job_id):
            job.mark_as_done()

    return render_template('/clientHomePage.html', **{'job_types': job_types,
                                                          'username': session.get('username')})

# client sterge job de tot
@app.route('/clientCancelRequest', methods=['POST'])
def cancel_request():
    job_id = request.form['list_index']
    to_remove = None

    for index, job in enumerate(global_dict['jobs']):
        if int(job.id) == int(job_id):
            to_remove = index

    global_dict['jobs'].pop(to_remove)

    return jobs_by_client()

@app.route('/clientHistory', methods=['GET'])
def done_jobs_for_client():
    done_jobs = [job for job in global_dict['jobs'] if job.client_username == session['username']
                 and job.done]

    return render_template('/clientHistory.html', **{'username': session.get('username'),
                                                         'jobs': done_jobs})

@app.route('/workerHistory', methods=['GET'])
def done_jobs_by_worker():
    current_user_id = get_current_user_id()
    done_jobs = [job for job in global_dict['jobs'] if job.worker_id == current_user_id and job.done]

    return render_template('/workerHistory.html', **{'username': session.get('username'),
                                                         'jobs': done_jobs})
# joburi initiate de clientul curent
@app.route('/clientJobs', methods=['GET'])
def jobs_by_client():
    jobs = [job for job in global_dict['jobs'] if job.client_username == session['username'] and not job.done]

    return render_template('/clientDisplayJobs.html', **{'username': session.get('username'),
                                                      'jobs': jobs})

# joburi asignate workerkului curent
@app.route('/workerJobs', methods=['GET'])
def jobs_by_worker():
    current_user_id = get_current_user_id()

    jobs = [job for job in global_dict['jobs'] if job.worker_id == current_user_id]
    return render_template('/workerDisplayJobs.html', **{'username': session.get('username'),
                                                      'jobs': jobs})

def get_current_user_id():
    for user in global_dict['users']:
        if user.username == session['username']:
            return user.id

def print_users():
    for user in global_dict['users']:
        print(user)

def print_jobs():
    for job in global_dict['jobs']:
        print(job)

if __name__ == '__main__':
    global_dict['users'] = []
    global_dict['jobs'] = []

    # asta e pt sesiune
    app.secret_key = os.urandom(12)

    # am bagat 3 useri si 3 joburi ca sa fie, daca mai vedeti erori, ziceti
    global_dict['users'].append(User(0, 'client1', 'cl1@local.com', '123', 'cl', '1', None,
                                     'desc', 'phone', 'Client', None))

    global_dict['users'].append(User(1, 'client2', 'cl2@local.com', '123', 'cl', '2', None,
                                     'desc', 'phone', 'Client', None))

    global_dict['users'].append(User(2, 'worker1', 'wo1@local.com', '123', 'wo', '1', None,
                                     'desc', 'phone', 'Worker', 'Instalator'))

    users_index = 3

    global_dict['jobs'].append(Job(0, 'Instalator', 'addr1', 'desc1', 'client1'))
    global_dict['jobs'].append(Job(1, 'Instalator', 'addr2', 'desc2', 'client2'))
    global_dict['jobs'].append(Job(2, 'Dadaca', 'addr3', 'desc3', 'client2'))
    jobs_index = 3

    app.run(debug=True)