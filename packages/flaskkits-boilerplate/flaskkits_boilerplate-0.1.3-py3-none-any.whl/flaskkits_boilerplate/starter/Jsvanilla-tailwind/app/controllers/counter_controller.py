from flask import render_template

def counter_view():
    return render_template('counter.html')
