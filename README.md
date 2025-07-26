# SOP Web App

This lightweight Flask application lets you upload SOPs written in Markdown
and walk through them step by step. The current step is shown one at a time
and once all steps are completed the SOP text is stored for later reference.

You can view previously executed SOPs from the **View Executed SOPs** link
on the upload page or by visiting `/history`.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000` in your browser.
