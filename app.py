from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime

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
            session['steps'] = steps
            session['index'] = 0
            session['original'] = content
            return redirect(url_for('steps'))
    return render_template('upload.html')


EXECUTED_FILE = "executed_sops.json"


def save_executed(md_text):
    """Append the executed SOP markdown to EXECUTED_FILE."""
    record = {"timestamp": datetime.utcnow().isoformat(), "content": md_text}
    data = []
    if os.path.exists(EXECUTED_FILE):
        with open(EXECUTED_FILE, "r", encoding="utf-8") as fh:
            try:
                data = json.load(fh)
            except json.JSONDecodeError:
                data = []
    data.append(record)
    with open(EXECUTED_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


@app.route('/steps', methods=['GET', 'POST'])
def steps():
    if 'steps' not in session:
        return redirect(url_for('upload'))

    index = session.get('index', 0)
    steps = session['steps']

    if request.method == 'POST':
        index += 1
        session['index'] = index
        session.modified = True

    if index >= len(steps):
        # SOP completed
        if session.get('original'):
            save_executed(session['original'])
        return render_template('steps.html', step=None, all_done=True)

    step_text = steps[index]
    return render_template('steps.html', step=step_text, index=index + 1, total=len(steps), all_done=False)


@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('upload'))


@app.route('/history')
def history():
    """Display executed SOPs."""
    entries = []
    if os.path.exists(EXECUTED_FILE):
        with open(EXECUTED_FILE, "r", encoding="utf-8") as fh:
            try:
                entries = json.load(fh)
            except json.JSONDecodeError:
                entries = []
    return render_template('history.html', entries=entries)


if __name__ == '__main__':
    app.run(debug=True)
