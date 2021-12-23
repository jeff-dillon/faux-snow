from flask import Flask, render_template, abort
import fauxsnow

app = Flask(__name__)
 
view_count = 0

@app.route("/")
def welcome():
    summary = fauxsnow.forecast_summary()
    return render_template("welcome.html", 
        ski_resorts=summary, 
        forecast_date=fauxsnow.forecast_date())

@app.route("/detail/<text_id>")
def detail(text_id):
    try:
        ski_resort = fauxsnow.load_ski_resort(text_id)
        print(ski_resort)
        return render_template("detail.html", 
            ski_resort=ski_resort, 
            forecast_date=fauxsnow.forecast_date(), 
            forecast=fauxsnow.resort_forecast(text_id))
    except IndexError:
        abort(404)