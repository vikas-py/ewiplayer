from flask import Flask, render_template, request, redirect, url_for, session
import markdown

app = Flask(__name__)
app.secret_key = 'change_this_secret'  # should be changed in production


def parse_steps(md_text):
    """Parse markdown text into a list of step strings."""
    lines = md_text.splitlines()
    steps = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('- ') or line.startswith('* '):
            step = line[2:].strip()
            steps.append(step)
        elif line[0].isdigit() and line[1:2] in {'.', ')'}:
            step = line[2:].strip()
            steps.append(step)
    return steps


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename:
            content = file.read().decode('utf-8')
            steps = parse_steps(content)
            session['steps'] = [{'text': s, 'done': False} for s in steps]
            session['original'] = content
            return redirect(url_for('steps'))
    return render_template('upload.html')


@app.route('/steps', methods=['GET', 'POST'])
def steps():
    if 'steps' not in session:
        return redirect(url_for('upload'))

    if request.method == 'POST':
        completed = request.form.getlist('step')
        for i, step in enumerate(session['steps']):
            step['done'] = str(i) in completed
        session.modified = True
    all_done = all(step["done"] for step in session["steps"])
    return render_template("steps.html", steps=session["steps"], all_done=all_done)


@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('upload'))


if __name__ == '__main__':
    app.run(debug=True)
