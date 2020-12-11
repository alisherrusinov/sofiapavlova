from flask import Flask, render_template, jsonify, request

app = Flask(__name__)



@app.route('/get_people', methods=['POST'])
def get_people():
    values = request.form.get('name')
    print(values)
    return jsonify('OK')

@app.route('/get_document', methods=['POST'])
def get_document():
    name = request.form.get('name')
    chin = request.form.get('chin')
    year = request.form.get('year')
    number = request.form.get('number')
    rubric = request.form.get('fubric')
    print(name)
    return jsonify('OK')

@app.route('/')
def hello_world():
    return render_template('index.html')




if __name__ == '__main__':
    app.run()
