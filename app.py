from flask import Flask, render_template, request, flash, redirect
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = 'l|F13?A-n)eWP(k'

# variables needed for dropdown menus and data functions
decades = [2020, 2040, 2060, 2080]
locations = ['Ann Arbor, MI', 'Annapolis, MD', 'Asheville, NC', 'Atlanta, GA', 'Augusta, ME', 'Austin, TX',
             'Bismarck, ND', 'Boise, ID', 'Boston, MA', 'Burlington, VT', 'Carson City, NV', 'Charleston, WV',
             'Cheyenne, WY', 'Chicago, IL', 'Columbia, SC', 'Columbus, OH', 'Concord, NH',
             'Denver, CO', 'Des Moines, IA', 'Dover, DE', 'Hartford, CT', 'Helena, MT', 'Indianapolis, IN',
             'Jackson, MS', 'Jefferson City, MO', 'Las Vegas, NV', 'Lincoln, NE', 'Little Rock, AR', 'Los Angeles, CA',
             'Louisville, KY', 'Madison, WI', 'Miami, FL', 'Montgomery, AL', 'Nashville, TN', 'New Orleans, LA',
             'New York, NY', 'Oklahoma City, OK', 'Philadelphia, PA', 'Phoenix, AZ', 'Pierre, SD', 'Portland, OR',
             'Providence, RI', 'Richmond, VA', 'Sacramento, CA', 'Saint Paul, MN', 'Salt Lake City, UT',
             'Santa Fe, NM', 'Seattle, WA', 'Tallahassee, FL', 'Topeka, KS', 'Trenton, NJ', 'Washington, DC']


# ----------------------- retirement score formulas in this section -------------------------------

def ave_temp_score(temp):
    """
    formula assessing deviation from ideal average
    annual temperature set at 75
    """
    score = 10 - (10 * abs(temp - 75) / 75)
    # return the score
    if score < 1:
        return 1
    elif score > 10:
        return 10
    else:
        return score


def pcpn_score(pcpn):
    """
    formula assessing deviation from average
    annual rainfall for the contiguous united states
    """
    score = 10 - (10 * abs(pcpn - 30.28) / 30.28)
    if score < 1:
        return 1
    elif score > 10:
        return 10
    else:
        return score


def extreme_temp_score(days):
    """
    formula assessing deviation from the ideal
    number of days with an extreme temperature
    i.e., max temp over 100°F or max temp below 32°F
    """
    if days == 0:
        return 10
    # lose half a point for every extreme temp day
    score = 10 - (days * .5)
    if score < 1:
        return 1
    elif score > 10:
        return 10
    else:
        return score


def dry_days_score(days):
    """
    formula assessing deviation from the average
    annual number of dry days for the united states
    """
    score = 10 - (10 * abs(days - 260) / 260)
    if score < 1:
        return 1
    elif score > 10:
        return 10
    else:
        return score


def retirement_score(tmax, tmin, pcpn, hot_days, cold_days, dry_days):
    """
    the average of all climate factors into one score
    """
    tmax_score = ave_temp_score(tmax)
    print('tmax score is', tmax_score)
    tmin_score = ave_temp_score(tmin)
    print('tmin_score is', tmin_score)
    precip_score = pcpn_score(pcpn)
    print('prcpn score is', precip_score)
    cold_score = extreme_temp_score(cold_days)
    print('cold score is', cold_score)
    hot_score = extreme_temp_score(hot_days)
    print('hot score is', hot_score)
    dry_score = dry_days_score(dry_days)
    print('dry score is', dry_score)

    total_score = round((tmax_score + tmin_score + precip_score +
                         cold_score + hot_score + dry_score) / 6)
    print('total score is', total_score)

    return total_score


# --------------------------- pandas climate data methods in this section -------------------------


def create_graph(location, file):
    """ creating a matplotlib graph for the location
        the graph will display projected max temps
    """
    # get the dataframe
    try:
        data = pd.read_csv(f'ClimateData/{location}/{file}_tmax.csv')
    except FileNotFoundError:
        print("Data not found.")
    else:
        # plot the data
        data.plot(0, [1, 4])
    # get ax to label the legend
    ax = plt.gca()
    ax.legend(["Low Emissions", "High Emissions"])
    # set the title
    location_title = location.title()
    # add a title
    plt.title("Projected Average Max Temperatures for {0}".format(location_title))
    # label the axes
    plt.ylabel("Average Daily Max Temp (°F)", labelpad=10)
    plt.xlabel("Years", labelpad=8)
    plt.minorticks_on()
    # save to an image to be pushed to website
    img = plt.savefig('static/plot.png')
    return img


def get_climate_data(location, decade, column, file):
    """
        getting the temp for location and decade
        at specified low/high emissions min/max column
    """
    # cast data to int
    decade = int(decade)
    # load .csv for location into dataframe
    try:
        df = pd.read_csv(f'ClimateData/{location}/{file}.csv')
    except FileNotFoundError:
        print("Data not found.")
    # set the index to year
    else:
        df.set_index('year', inplace=True)
        # get max temp low emissions for year
        data = df.at[decade, column]
        # return the data
        return data


def get_natural_disasters(location, disaster):
    """ get the natural disasters data for location """
    try:
        df = pd.read_csv(f'ClimateData/natural_disasters.csv')
    except FileNotFoundError:
        print("Data not found.")
    else:
        # set the index to city
        df.set_index('Capital', inplace=True)
        # get the likelihood of disaster
        data = df.at[location, disaster]
        return data


# --------------------------- app routes in this section ------------------------------------


@app.route('/')
@app.route('/home')
def index():
    """using global variables for decades and locations"""
    return render_template('home.html', decades=decades, locations=locations)


@app.route('/results', methods={'GET', 'POST'})
def post_results():
    """ post the results from the search """
    # get location and decade from form
    location = request.form.get('locations')
    decade = request.form.get('decades')
    # error handling
    if location == '' or location == 'location' or location is None:
        flash("You must choose a location.")
        return redirect('/')
    elif decade == '' or decade == 'decade' or decade is None:
        flash("You must choose a decade.")
        return redirect('/')
    else:
        # format the location names for filenames
        city = location.split(",")[0].replace(",", "")
        filename = city.replace(" ", "_").lower()
    # draw a graph of temperature projections for location
    create_graph(city, filename)
    # get the low emissions temp data
    le_min_temp = get_climate_data(city, decade, ' rcp45_weighted_mean', filename + "_tmin")
    le_max_temp = get_climate_data(city, decade, ' rcp45_weighted_mean', filename + "_tmax")
    le_hot_days = round(get_climate_data(city, decade, ' rcp45_weighted_mean', filename + "_100f"))
    le_cold_days = round(get_climate_data(city, decade, ' rcp45_weighted_mean', filename + "_32f"))
    # get the high emissions temp data
    he_min_temp = get_climate_data(city, decade, ' rcp85_weighted_mean', filename + "_tmin")
    he_max_temp = get_climate_data(city, decade, ' rcp85_weighted_mean', filename + "_tmax")
    he_hot_days = round(get_climate_data(city, decade, ' rcp85_weighted_mean', filename + "_100f"))
    he_cold_days = round(get_climate_data(city, decade, ' rcp85_weighted_mean', filename + "_32f"))
    # get the precipitation data
    le_dry_days = round(get_climate_data(city, decade, ' rcp45_weighted_mean', filename + "_dry_days"))
    he_dry_days = round(get_climate_data(city, decade, ' rcp85_weighted_mean', filename + "_dry_days"))
    le_pcpn = get_climate_data(city, decade, ' rcp45_weighted_mean', filename + "_pcpn")
    he_pcpn = get_climate_data(city, decade, ' rcp85_weighted_mean', filename + "_pcpn")
    # get the natural disasters data
    earthquakes = get_natural_disasters(city, 'Earthquakes')
    hurricanes = get_natural_disasters(city, 'Hurricanes')
    wild_fires = get_natural_disasters(city, 'Wild Fires')
    tornadoes = get_natural_disasters(city, 'Tornadoes')
    # get the retirement score
    # tmax, tmin, pcpn, hot_days, cold_days, dry_days
    le_score = retirement_score(le_max_temp, le_min_temp, le_pcpn, le_hot_days, le_cold_days, le_dry_days)
    he_score = retirement_score(he_max_temp, he_min_temp, he_pcpn, he_hot_days, he_cold_days, he_dry_days)
    ave_score = round((le_score + he_score) / 2)
    # send to results page
    return render_template('results.html', location=location, decade=decade,
                           le_min_temp=le_min_temp, le_max_temp=le_max_temp,
                           he_min_temp=he_min_temp, he_max_temp=he_max_temp,
                           le_hot_days=le_hot_days, he_hot_days=he_hot_days,
                           le_cold_days=le_cold_days, he_cold_days=he_cold_days,
                           le_dry_days=le_dry_days, he_dry_days=he_dry_days,
                           le_pcpn=le_pcpn, he_pcpn=he_pcpn,
                           earthquakes=earthquakes, hurricanes=hurricanes,
                           wild_fires=wild_fires, tornadoes=tornadoes,
                           ave_score=ave_score)


@app.route('/about')
def about():
    """ the about page tells the user about the application """
    return render_template('about.html')


@app.route('/interactive_map')
def interactive_map():
    """ displays the interactive map page """
    return render_template('interactive_map.html')


def main():
    print('hi')


if __name__ == '__main__':
    main()
