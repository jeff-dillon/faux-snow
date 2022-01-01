from flask import Flask, render_template, abort
import fauxsnow

app = Flask(__name__)
 
view_count = 0

@app.route("/")
def welcome():
    resorts = fauxsnow.load_ski_resorts()
    forecasts = fauxsnow.load_forecasts_from_file()
    return render_template("welcome.html", 
        combined = fauxsnow.combine_resorts_forecasts(resorts, forecasts),
        forecast_date=fauxsnow.forecasts_date(forecasts))

@app.route("/detail/<text_id>")
def detail(text_id):
    try:
        resort = fauxsnow.load_ski_resort(text_id)
        forecast = fauxsnow.load_forecast_from_file(text_id)
        return render_template("detail.html", 
            combined = fauxsnow.combine_resort_forecast(resort, forecast, text_id), 
            forecast_date=fauxsnow.forecast_date(forecast))
    except IndexError:
        abort(404)

@app.route("/refresh")
def refresh():
    resorts = fauxsnow.load_ski_resorts()
    forecasts = fauxsnow.load_forecasts_from_api(resorts)
    # if the api call returns None, fail gracefully.
    message = ''
    if forecasts:
        fauxsnow.save_forecasts(forecasts)
        message = 'Updated forecasts'
    else:
        message = 'could not update forecasts'
    return render_template('refresh.html', message=message)

@app.route("/about")
def abour():
    return render_template("about.html")
