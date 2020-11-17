
from flask import Flask,render_template,request,redirect,url_for
from flask_classful import FlaskView
import json
app = Flask(__name__)

class FormView(FlaskView):
    default_methods = ['GET','POST']
    route_base='/'

    def index(self):
        return redirect(url_for('FormView:info'))
    def info(self):
        if request.method == 'POST':
            P.Name = request.form["Name"]
            P.Mail = request.form["Emailid"]
            P.Phno = request.form["Phno"]
            print(P.Name,P.Mail,P.Phno)
            mail_list(P.Name,P.Mail,P.Phno)
        return render_template("form.html")


def mail_list(name,mail,no,filename='mailing_list.json'):
    with open('mailing_list.json') as json_file: 
        data = json.load(json_file) 
        temp = data['list'] 
        y = {"name": name, 
            "email": mail,
            "phno": no
            }        
        temp.append(y) 
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4)

FormView.register(app)

class Person():
    pass
P = Person()

if __name__ == '__main__':
    app.run(debug=True)
