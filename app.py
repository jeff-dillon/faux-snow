from flask import Flask, render_template, abort
import fauxsnow

app = Flask(__name__)
 
view_count = 0

@app.route("/")
def welcome():
    return render_template("welcome.html", 
        combined=fauxsnow.combine_resorts_forecasts(fauxsnow.load_ski_resorts(), fauxsnow.load_forecasts_from_file()),
        forecast_date=fauxsnow.forecast_date())

@app.route("/detail/<text_id>")
def detail(text_id):
    try:
        return render_template("detail.html", 
            combined=fauxsnow.combine_resort_forecast(fauxsnow.load_ski_resorts(), fauxsnow.load_forecasts_from_file(), text_id), 
            forecast_date=fauxsnow.forecast_date())
    except IndexError:
        abort(404)