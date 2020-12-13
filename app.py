from flask import Flask, render_template, jsonify, request, send_file
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from flask_mail import Mail, Message
from celery import Celery
from celery.schedules import crontab
import json

HOST = 'http://127.0.0.1:5000' # Адрес хостинга (нужно для рассылки)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' # Имя базы данных
app.config['MAIL_SERVER'] = 'smtp.googlemail.com' # Адрес почтогого сервера google
app.config['MAIL_PORT'] = 587 # Порт сервера
app.config['MAIL_USE_TLS'] = True # Настройка безопасности для отправки почты
app.config['MAIL_USERNAME'] = 'mail@gmail.com'  # введите свой адрес электронной почты здесь
app.config['MAIL_DEFAULT_SENDER'] = 'mail@gmail.com'  # и здесь
app.config['MAIL_PASSWORD'] = 'password'  # введите пароль
db = SQLAlchemy(app) # Объект менеджера базы данных
mail = Mail(app) # Объект менеджера почты

def make_celery(app):
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379' # Настройка для брокера celery
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379' # Настройка для бэкенда celery
    app.config['CELERYBEAT_SCHEDULE'] = { # Настройка расписания включения функции проверки нового файла
        'check_new_files-every-day': {
            'task': 'check_new_files',
            'schedule': crontab(minute='*'),#hour=24 на дебаге можно использовать minute(чтобы не ждать 24 часа). В продакшене предполагается hour=24
        }
    }
    app.config['TIMEZONE'] = 'UTC' # Настройка часогого пояса для расписания celery
    celery = Celery( # Создание объекта celery
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config) # Обновление настроек celery в соответствии с настройками приложения

    class ContextTask(celery.Task): # Создание задачи(для работы celery)
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask # Установки задачи для celery
    return celery


celery = make_celery(app) # Создание объекта celery с помощью вышеописанной функции


class ManModel(db.Model): # Модель человека для базы  данных
    id = db.Column(db.Integer, primary_key=True) # Его айди
    name = db.Column(db.String(100), nullable=False) # Имя
    old_name = db.Column(db.String(200), nullable=False) # Имя по старому стилю
    chin = db.Column(db.String(100), nullable=False) # Чин
    rubric = db.Column(db.String(100), nullable=False) # Специальная рубрика
    tables = db.relationship('RelatedInfo', backref='person', lazy=True) # Связанные с ним записи в архивах


class RelatedInfo(db.Model): # Модель записи в архиве
    id = db.Column(db.Integer, primary_key=True) # Айди
    year = db.Column(db.String(100), nullable=False) # Год записи
    note = db.Column(db.String(200)) # Текст пометы
    count = db.Column(db.Integer) # Количество дворов
    list_number = db.Column(db.Integer) # Номер листа
    arch_note = db.Column(db.String(200)) # Археографическое примечание
    person_id = db.Column(db.Integer, db.ForeignKey('man_model.id'), # Привязка к человеку
                          nullable=False)


class FileModel(db.Model): # Модель публикации
    id = db.Column(db.Integer, primary_key=True) # Айди
    name = db.Column(db.String(200), nullable=False, unique=True) # Название публикации(которое будет на сайте)
    location = db.Column(db.String(200), nullable=False, unique=True) # Название файла(который лежит в папке на сервере)


class MailModel(db.Model): # Модель email для рассылки
    id = db.Column(db.Integer, primary_key=True) # Айди
    mail = db.Column(db.String(200), nullable=False, unique=True) # Электронная почта


@celery.task(name='check_new_files') # Помечание для celery, что эту функцию нужно выполнять каждые n времени
def check_new_files():
    file = open('last.txt') # Получение последнего ->
    last = int(file.read()) # Айди
    current = FileModel.query.all()[-1].id # Получение последнего айди в базе данных
    if(current>last): # Если новая публикация
        mailing() # Запустить процесс рассылки
        file.write(str(current)) # Обновить данные
        file.close()


def mailing():
    mails_query = MailModel.query.all() # Получение всех записей email в базе данных
    mails = [] # Список только email'ов
    for i in mails_query:
        mails.append(i.mail) # Добавление имейлов в список
    for email in mails: # Проход по всему списку имейлов
        msg = Message("Новая публикация", recipients=[email]) # Создание сообщения
        unfollow = f"{HOST}/email_unfollow?mail={email}" # Создание ссылки на отписку от рассылки
        msg.html = f'<h2>Добрый день!</h2>\n<p>Доступна новая публикация на сайте "Боярские списки XVIII века".</p>\n<p>Вы получили это письмо, так как подписались на уведомление о новых публикациях</p>\n<a href="{unfollow}">Отписаться от рассылки</a>'# Текст сообщения
        mail.send(msg)# Отправка сообщения


@app.route('/files/<file_name>')
def get_file(file_name):
    """Функция обрабатывающая запрос на загрузку файла"""
    try:
        return send_file(f'files/{file_name}', as_attachment=True) # Отправка файла
    except Exception as e: # Если файла не существует вернуть 404
        print(e)
        return 404


@app.route('/get_people', methods=['POST'])
def get_people():
    """Обработчик ajax запроса по поиску людей по критериям"""

    name = request.form.get('name')
    chin = request.form.get('chin')
    rubric = request.form.get('rubric')

    parameters_dirty = [name, chin, rubric]  # Параметры с возможно незаполненными полями
    parameters = []
    for i in parameters_dirty:  # Очищение списка параметров запроса от пустых полей
        if (i is not None):
            parameters.append(i)
    del parameters_dirty

    # Далее следует запрос к базе данных напрямую через SQL, т.к. через ORM нельзя сделать неизвестное кол-во параметров
    query = "select * from man_model where"  # шаблон запроса к базе данных
    for index, parameter in enumerate(parameters):
        if (index == 0):  # Если первый элемент списка необработанных аргументов
            # Такие проверки необходимо провести, т.к. в списке неизвестно, какой элемент чем является(именем, чином и т.д)
            if (parameter == name):
                query = f'select * from man_model where name="{parameter}" '  # Все это нужно для того чтобы в запросе ставить в зависимости от параметров разные критерии поиска
            elif (parameter == chin):
                query = f'select * from man_model where chin="{parameter}" '
            else:
                query = f'select * from man_model where rubric="{parameter}" '
        else:
            # Все тоже самое, но для остальных элементов необработанного списка
            if (parameter == name):
                query = f'{query} and name="{parameter}" '
            elif (parameter == chin):
                query = f'{query} and chin="{parameter}" '
            else:
                query = f'{query} and rubric="{parameter}" '
    man = db.engine.execute(query)  # Обращение к базе данных
    man = [x for x in man]  # Преобразование объекта запроса к базе данных в привычный список
    print(man)
    if (len(man) == 0):
        return jsonify(404)
    response = []
    for i in man:
        response.append(list(i))
    print(json.dumps(response, ensure_ascii=False))
    return json.dumps(response,ensure_ascii=False, )  # Отправка ответа в формате JSON. Параметр ensure_ascii нужен для того чтобы не было путаницы с кодировкой


@app.route('/people_info/<id>')
def man_detail(id):
    """Функция обработчик запроса к персональной странице человека"""
    man = ManModel.query.get_or_404(id)  # Получение модели человека
    tables = RelatedInfo.query.filter_by(person_id=id).all()  # Получение связанных с ним записей в таблицах(архивах)
    return render_template('man_detail.html', man=man, tables=tables)


@app.route('/')
def index():
    """Функция обработчик запроса в корень сайта"""
    all_people = ManModel.query.all() # Получение списка людей (нужно для формирования подсказок в формах)
    all_chins = [] # Все чины(подсказка для формы поиска по чинам)
    all_rubrics = [] # Все рубрики(подсказка для формы поиска по рубрикам)
    all_names = [] # Все имена(подсказка для формы поиска по именам)
    for i in all_people:
        all_chins.append(i.chin) # Добавление чина в список
        all_rubrics.append(i.rubric) # Добавление рубрики в список
        all_names.append(i.name) # Добавление имени в список
    return render_template('index.html', all_names=all_names, all_chins=all_chins, all_rubrics=all_rubrics)


@app.route('/publications')
def all_publications():
    """Функция обработчик запроса в список всех публикаций"""
    all_files = FileModel.query.all() # Все публикации
    return render_template('all_files.html', all_files=all_files)


@app.route('/about')
def about():
    """Функция обработчик запроса в раздел о сайте"""
    return render_template('about.html')


@app.route('/email_unfollow')
def unfollow():
    """Функция обработчик запроса на отписку от рассылки"""
    email = request.args.get('mail') # Получить email из аргументов запроса
    email_model = MailModel.query.filter_by(mail=email).all()[0] # Получить соответствующую ему модель из базы данных
    db.session.delete(email_model) # Удалить модель
    db.session.commit() # Сохранить изменения
    return 'Вы успешно отписались от рассылки'


@app.route('/email_follow', methods=['POST'])
def follow():
    """Функция обработчик запроса на подписку на рассылку"""
    email = request.form.get('mail') # Получение email из аргументов запроса
    try: # Попытаться добавить в базу данных
        email_model = MailModel(mail=email) # Создать объект email
        db.session.add(email_model) # Добавить в бд
        db.session.commit() # Сохранить изменения
    except sqlalchemy.exc.IntegrityError: # Если такая запись уже существует
        return jsonify('error') # Вернуть ошибку
    return jsonify('OK') # Если успешно то вернуть ОК


@app.route('/help')
def help_():
    """Функция обработчик запроса в раздел помощь сайта"""
    return render_template('help.html')


if __name__ == '__main__':
    app.run()
