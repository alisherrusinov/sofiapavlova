from flask import Flask, render_template, jsonify, request, send_file
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class ManModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    old_name = db.Column(db.String(200), nullable=False)
    chin = db.Column(db.String(100), nullable=False)
    rubric = db.Column(db.String(100), nullable=False)
    tables = db.relationship('RelatedInfo', backref='person', lazy=True)


class RelatedInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(100), nullable=False)
    note = db.Column(db.String(200))
    count = db.Column(db.Integer)
    list_number = db.Column(db.Integer)
    arch_note = db.Column(db.String(200))
    person_id = db.Column(db.Integer, db.ForeignKey('man_model.id'),
                          nullable=False)


class FileModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    location = db.Column(db.String(200), nullable=False, unique=True)


@app.route('/get_document', methods=['POST'])
def get_document():
    value = request.form.get('value')
    print(value)
    file = FileModel.query.filter_by(name=value).first()
    print(file)

    if(file == None):
        return jsonify(404)
    else:
        return jsonify([file.name, file.location])


@app.route('/files/<file_name>')
def get_file(file_name):
    try:
        return send_file(f'files/{file_name}', as_attachment=True)
    except Exception as e:
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
    return json.dumps(response,
                      ensure_ascii=False, )  # Отправка ответа в формате JSON. Параметр ensure_ascii нужен для того чтобы не было путаницы с кодировкой


@app.route('/people_info/<id>')
def man_detail(id):
    """Функция обработчик запроса к персональной странице человека"""
    man = ManModel.query.get_or_404(id)  # Получение модели человека
    tables = RelatedInfo.query.filter_by(person_id=id).all()  # Получение связанных с ним записей в таблицах(архивах)
    return render_template('man_detail.html', man=man, tables=tables)





@app.route('/')
def hello_world():
    """Функция обработчик запроса в корень сайта"""
    all_people = ManModel.query.all()
    all_chins = []
    all_rubrics = []
    all_names = []
    for i in all_people:
        all_chins.append(i.chin)
        all_rubrics.append(i.rubric)
        all_names.append(i.name)
    return render_template('index.html', all_names=all_names, all_chins=all_chins, all_rubrics=all_rubrics)

@app.route('/publications')
def all_publications():
    """Функция обработчик запроса в корень сайта"""
    all_files = FileModel.query.all()
    return render_template('all_files.html', all_files=all_files)


@app.route('/about')
def about():
    """Функция обработчик запроса в корень сайта"""
    return render_template('about.html')

@app.route('/help')
def help_():
    """Функция обработчик запроса в корень сайта"""
    return render_template('help.html')


if __name__ == '__main__':
    app.run()
