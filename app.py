from flask import Flask, render_template, request
from construct_listops_tree import parse_single_data
# from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

# App config.
app = Flask(__name__)

@app.route('/tree', methods=['POST', 'GET'])
def show_tree():
    error = None
    json_string = ""
    data = ""
    if request.method == 'POST':
        data = request.form['data']
        json_string = parse_single_data(data)

    return render_template('tree.html', data=data, tree_json_string = json_string)

@app.route("/hello")
def hello():
    return render_template('hello.html')

if __name__ == "__main__":
    app.run()
