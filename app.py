from flask import Flask, render_template, abort
import fauxsnow

app = Flask(__name__)
 
view_count = 0

@app.route("/")
def welcome():
    summary = fauxsnow.forecast_summary()
    return render_template("welcome.html", ski_resorts=summary, forecast_date=fauxsnow.forecast_date())

@app.route("/detail/<int:index>")
def detail(index):
    try:
        ski_resort = fauxsnow.forecast_summary()[index-1]
        return render_template("detail.html", ski_resort=ski_resort)
    except IndexError:
        abort(404)