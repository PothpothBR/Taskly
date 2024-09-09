from flask import render_template, redirect, url_for
from config import app, db
from models import User, Task
from flask_login import login_required, login_user, logout_user, current_user
from forms import RegisterForm, LoginForm, TaskForm
from werkzeug.security import generate_password_hash, check_password_hash


@app.route('/')
def home():
    return redirect(url_for('dashboard'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        psswd = generate_password_hash(form.password.data)

        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('register.html', form=form, error='Usuário ja existe')

        user = User(username=username, psswd=psswd)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()

        if user:
            psswd = form.password.data
            hashPsswd = user.psswd

            if check_password_hash(hashPsswd, psswd):
                login_user(user)
                return redirect(url_for('dashboard'))

        return render_template('login.html', form=form, error="Usuário ou senha incorretos")
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def add_assignee(t: Task):
    assignee: User = User.query.filter_by(id=t.assignee_id).first()
    return type('POJOTaskAssignee', (object,), {
        'id': t.id,
        'title': t.title,
        'task_date': t.task_date,
        'desc': t.desc,
        'status': t.status,
        'user_id': t.user_id,
        'assignee_id': t.assignee_id,
        'assignee': assignee.username,
    })()

@app.route('/dashboard')
@login_required
def dashboard():
    
    return render_template('dashboard.html',
        my_tasks=list(map(add_assignee, Task.query.filter_by(user_id=current_user.id))),
        all_tasks=list(map(add_assignee, Task.query.all()))
    )


@app.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():

    form = TaskForm()
    form.task_assignee.choices = list(map(lambda u: (u.id, u.username), User.query.all()))
    form.task_status.choices = ["Pendente", "Em Andamento", "Concluida"]

    if form.validate_on_submit():
        taskname = form.task_title.data
        task = Task.query.filter_by(title=taskname).first()
        if task:
            return render_template('create_task.html', form=form, error="Tarefa já existe")
        else:
            assignee = User.query.filter_by(id=form.task_assignee.data).first()

            if (not assignee):
                return render_template('create_task.html', form=form, error="Usuário inexistente")


            title = form.task_title.data
            task_date = form.task_date.data
            desc = form.description.data
            assignee_id = assignee.id
            status = form.task_status.data
            user_id = current_user.id
            newTask = Task(title=title, assignee_id=assignee_id, status=status, task_date=task_date, desc=desc, user_id=user_id)
            db.session.add(newTask)
            db.session.commit()
            return redirect(url_for('dashboard'))

    return render_template('create_task.html', form=form)


@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    form = TaskForm()
    form.task_assignee.choices = list(map(lambda u: (u.id, u.username), User.query.all()))
    form.task_status.choices = ["Pendente", "Em Andamento", "Concluida"]
    form.submit.label.text = 'Editar Task'

    if form.validate_on_submit():
        print(form.task_assignee.data)        
        task = Task.query.filter_by(id=id).first()
        task.title = form.task_title.data
        task.task_date = form.task_date.data
        task.desc = form.description.data
        task.assignee_id = form.task_assignee.data
        db.session.commit()
        return redirect(url_for('dashboard'))

    task = Task.query.filter_by(id=id).first()
    form.task_title.data = task.title
    form.task_date.data = task.task_date
    form.description.data = task.desc
    form.task_assignee.data = str(task.assignee_id)

    return render_template('edit_task.html', form=form)


@app.route('/delete_task/<int:id>', methods=['POST'])
@login_required
def delete_task(id):
    print(id)
    Task.query.filter_by(id=id).delete()
    db.session.commit()

    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
