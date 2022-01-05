from flask import Flask, render_template, abort
from fauxsnow import ResortModel, ForecastAPILoader, ForecastModel

app = Flask(__name__)
 
view_count = 0

@app.route("/")
def welcome():

    resort_model = ResortModel()
    resorts = resort_model.get_all_resorts()
    return render_template("welcome.html", resorts=resorts)

@app.route("/detail/<text_id>")
def detail(text_id):
    try:
        resort_model = ResortModel()
        resort = resort_model.get_resort_by_id(text_id)
        if resort:
            return render_template("detail.html", resort=resort)
        else:
            abort(500)
    except IndexError:
        abort(404)

@app.route("/refresh")
def refresh():
    rm = ResortModel()
    fm = ForecastModel()
    resorts = rm.get_all_resorts()
    fAPI = ForecastAPILoader()
    forecasts = fAPI.load_forecasts_from_api(resorts)
    # if the api call returns None, fail gracefully.
    message = ''
    if forecasts:
        fm.save_forecasts(forecasts)
        message = 'Updated forecasts'
    else:
        message = 'could not update forecasts'
    return render_template('refresh.html', message=message)

@app.route("/about")
def about():
    rm = ResortModel()
    resorts = rm.get_all_resorts()
    num_resorts = len(resorts)
    return render_template("about.html", resorts=resorts, num_resorts=num_resorts)

@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404 Not Found'), 404

@app.errorhandler(500)
def page_not_found(error):
   return render_template('404.html', title = 'Something went wrong'), 500
 
