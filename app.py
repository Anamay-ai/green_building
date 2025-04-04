
from flask import Flask, render_template, request, redirect, url_for, session
import joblib

app = Flask(__name__)
app.secret_key = 'supersecretkey'
model = joblib.load('logistic_model.pkl')

questions = [
    {"id": "cost", "text": "How much do cost concerns affect your decision to pursue GRS certification?", "type": "scale"},
    {"id": "awareness", "text": "How would you rate your awareness of Green Rating Systems (e.g., GRIHA, IGBC, LEED)?", "type": "scale"},
    {"id": "training", "text": "Have you or your team received any formal training on Green Rating Systems?", "type": "binary"},
    {"id": "regulatory", "text": "Are you aware of any regulatory incentives for implementing Green Rating Systems?", "type": "binary"},
    {"id": "experience", "text": "How many years of experience do you have in the construction industry?", "type": "numeric"},
    {"id": "project", "text": "What is the type of project you are currently working on?", "type": "binary_text", "options": ["Residential", "Commercial"]},
    {"id": "client", "text": "Is your client willing to pay extra for GRS certification?", "type": "binary"},
]

@app.route("/")
def home():
    session.clear()
    return render_template("home.html")

@app.route("/start")
def start():
    return redirect(url_for("question", step=0))

@app.route("/question/<int:step>", methods=["GET", "POST"])
def question(step):
    if step >= len(questions):
        return redirect(url_for("result"))
    if request.method == "POST" and step > 0:
        session[questions[step - 1]["id"]] = request.form.get(questions[step - 1]["id"])
    return render_template("question.html", question=questions[step], step=step, total=len(questions))

@app.route("/result")
def result():
    inputs = []
    for q in questions:
        val = session.get(q["id"])
        if q["type"] in ['scale', 'numeric']:
            inputs.append(int(val))
        elif q["type"] == "binary":
            inputs.append(1 if val == "yes" else 0)
        elif q["type"] == "binary_text":
            inputs.append(1 if val == "Commercial" else 0)
    pred = model.predict([inputs])[0]
    prob = model.predict_proba([inputs])[0][1]
    return render_template("result.html", prediction=pred, probability=round(prob*100, 1))

if __name__ == "__main__":
    app.run(debug=True)
