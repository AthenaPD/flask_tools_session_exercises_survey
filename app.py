from flask import Flask, render_template, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys, Survey, Question

app = Flask(__name__)
app.config["SECRET_KEY"] = "Orion"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)


@app.route("/")
def home_page():
    if not session.get('responses', None):
        session['responses'] = {key: [] for key in surveys.keys()}
    return render_template("home_page.html")

@app.route("/add_survey")
def add_survey():
    return render_template("add_survey.html")

@app.route("/create_survey", methods=["POST"])
def create_survey():
    # get answers from form
    name = request.form['name'].replace(" ","-")
    title = request.form['title']
    instructions = request.form['instruction']

    # Get the total number of questions from the last charater of the last key in the request.form dictionary
    form_dict = request.form
    num_question = int(list(form_dict.keys())[-1][-1])

    # Make questions
    questions = []
    for i in range(1, num_question + 1):
        question = request.form[f'q{i}']
        choices = [ans.strip() for ans in request.form[f'choice{i}'].split(",")] if request.form[f'choice{i}'] else None
        allow_text = True if request.form.get(f'comment{i}', None) else False
        questions.append(Question(question=question, choices=choices, allow_text=allow_text))

    # Make survey
    surveys[name] = Survey(title=title, instructions=instructions, questions=questions)

    # Update cookies
    responses = session['responses']
    responses[name] = []
    session['responses'] = responses

    # Flash user and return to home page
    flash("A new survey was added!")
    return redirect("/")

@app.route("/choose_survey")
def choose_survey():
    return render_template("choose_survey.html", surveys=surveys)

@app.route("/start_survey")
def survey_start_page():
    if request.args.get("survey", None):
        survey_name = request.args['survey']
        survey = surveys[survey_name]
        return render_template("start_page.html", survey=survey, survey_name=survey_name)
    else:
        flash("Please select a survey to start!")
        return redirect("/")

@app.route("/<survey_name>", methods=["POST"])
def start_survey(survey_name):
    return redirect(f"/{survey_name}/questions/0")

@app.route("/<survey_name>/questions/<int:id>")
def show_questions(survey_name, id):
    survey = surveys[survey_name]
    responses = session["responses"]
    current_question_num = len(responses[survey_name])
    if current_question_num == len(survey.questions):
        flash("You have already completed the survey.")
        return redirect(f"/{survey_name}/thanks")
    
    if id > current_question_num or id < 0:
        flash("You are trying to access an invalid page.")
        return redirect(f"/{survey_name}/questions/{current_question_num}")
    
    return render_template("survey_questions_form.html", id=id, question=survey.questions[id], survey_name=survey_name)

@app.route("/<survey_name>/answer/<int:id>", methods=["POST"])
def answer_questions(survey_name, id):
    survey = surveys[survey_name]
    responses = session["responses"]
    ans = request.form.get("choice", "")
    if request.form.get("comment", None):
        comment = request.form["comment"]
        ans = [ans, comment]
    if id < len(responses[survey_name]):
        responses[survey_name][id] = ans
    else:
        responses[survey_name].append(ans)
    session['responses'] = responses
    next_page = f"/{survey_name}/questions/{id+1}" if id+1 < len(survey.questions) else f"/{survey_name}/thanks"
    return redirect(next_page)

@app.route("/<survey_name>/thanks")
def thank_you(survey_name):
    survey = surveys[survey_name]
    ans = session['responses'][survey_name]
    ans = [" -> ".join(a) if isinstance(a, list) else a for a in ans]
    return render_template("thanks.html", questions=survey.questions, ans=ans)
