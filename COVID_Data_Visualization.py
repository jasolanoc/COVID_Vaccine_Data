import os
import csv
os.environ['PROJ_LIB'] = r'C:\Users\alejj\miniconda3\envs\6.86x\Lib\site-packages'
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

'''

DESCRIPTION

This program allows to visualize the percentage of people how have at least received one vaccination doses around the
world. To check individual countries just type the name (in English) otherwise, if you want to check the whole world type
Global.

The data is recovered from the John Hopkins University. Missing population and geographic locations were complemented 
with Wikipedia. 

You can dowload the data at: https://github.com/govex/COVID-19

The data presented here corresponds to the reported data on the May 27th, 2021

'''

MARKER_SZ_SCALE = 1/50000

def main():

    '''
    Asks the user for a country. If the user´s input is global, it gets the data for all the countries, otherwise
    it gets only the data for the requested country. If the user´s input is not a valid country, the program asks for
    new input until it receives a valid input
    '''

    countries_list = get_countries_list()
    countries_list.append('Global')

    country = input('Select a country to visualize it´s associated vaccination progress: ')
    while country not in countries_list:
        print('')
        print('The name of the country is not registered in the database or is written incorrectly')
        country = input('Please try again: ')

    if country == 'Global':

        countries_list.pop()

    else:

        countries_list = [country]

    lat = []
    long = []
    vaccine_percentage = []
    population = []

    for countries in countries_list:

        country_data = get_vaccine_data(countries)
        get_population_data(countries, country_data)

        if len(country_data) > 1:
            if '' in country_data:
                del country_data['']

        lat, long, vaccine_percentage, population = process_country_data(country_data, lat, long, vaccine_percentage,
                                                                         population)

    plot_map(country, lat, long, vaccine_percentage, population)


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


def get_countries_list():

    '''
    Gets a list of the countries that are registered in the database
    '''

    with open("Vaccines_Data_Global.csv") as f:
        reader = csv.DictReader(f)
        countries_list = []

        for line in reader:
            countries_list.append(line['Country_Region'])

    return countries_list


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


def get_vaccine_data(country):

    '''
    Returns the associated administered doses of COVID vaccines per Province/State.
    '''

    # Specific database for the US

    if country == 'US':

        with open("Vaccines_Data_US.csv") as f:
            reader = csv.DictReader(f)
            country_data = {}

            for line in reader:
                if line['Province_State'] in country_data:
                    country_data[line['Province_State']][0] += float(line['Doses_admin'])
                else:
                    country_data[line['Province_State']] = [float(line['Doses_admin'])]

    # Database for other countries

    else:

        with open("Vaccines_Data_Global.csv") as f:
            reader = csv.DictReader(f)
            country_name = country
            country_data = {}

            for line in reader:
                if line['Country_Region'] == country_name:
                    country_data[line['Province_State']] = [float(line['Doses_admin'])]

    return country_data


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


def get_population_data(country, country_data):

    '''
    Once the country has been selected, the function adds information related to latitude, longitude and population for
    eache Province/Region to the dictionary
    '''

    # Specific database for the US

    if country == 'US':

        with open("Vaccines_Data_US_Population.csv") as f:
            reader = csv.DictReader(f)

            for line in reader:
                if line['Province_State'] in country_data:
                    country_data[line['Province_State']].append(float(line['Lat']))
                    country_data[line['Province_State']].append(float(line['Long_']))
                    country_data[line['Province_State']].append(float(line['Population']))

    # Database for other countries

    else:

        with open("Vaccines_Data_Global_Population.csv") as f:
            reader = csv.DictReader(f)

            for line in reader:
                if line['Country_Region'] == country and line['Province_State'] in country_data:
                    country_data[line['Province_State']].append(float(line['Lat']))
                    country_data[line['Province_State']].append(float(line['Long_']))
                    country_data[line['Province_State']].append(float(line['Population']))


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


def get_lat_long(country, lat, long):

    '''
    Determines the region (latitude and longitude) in which to plot the associated vaccine data
    '''

    LAT_BORDER = 10
    LONG_BORDER = 12.5

    if country != 'Global':

        max_lat = max(lat) + LAT_BORDER
        min_lat = min(lat) - LAT_BORDER
        max_long = max(long) + LONG_BORDER
        min_long = min(long) - LONG_BORDER

        return max_lat, min_lat, max_long, min_long

    else:

        return 90, -70, 180, -180


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

def process_country_data(country_data, lat, long, vaccine_percentage, population):

    '''
    Process the country data to extract the latitude, longitude, percentage of population vaccinated and population per
    region/state in each country
    '''

    for region in country_data.keys():
        lat.append(country_data[region][1])
        long.append(country_data[region][2])
        # Divided by two because vaccines are administered twice per person (two doses)
        vaccine_percentage.append(100*country_data[region][0]/(2*country_data[region][3]))
        population.append(MARKER_SZ_SCALE*country_data[region][3])

    return lat, long, vaccine_percentage, population


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

def plot_map(country, lat, long, vaccine_percentage, population):

    '''
    Plots the associated map for the input data
    '''

    max_lat, min_lat, max_long, min_long = get_lat_long(country, lat, long)

    map = Basemap(projection='mill', resolution='i',
                  llcrnrlat=min_lat, urcrnrlat=max_lat, llcrnrlon=min_long, urcrnrlon=max_long)
    map.drawcountries(linewidth=0.75)
    map.shadedrelief()

    if country == 'Global':
        population[:] = [ x / 7.5  for x in population]

    map.scatter(long, lat, latlon=True, c=vaccine_percentage, cmap='RdYlGn', s = population, alpha=0.75)
    plt.clim(0, 100)
    plt.colorbar(label='Percentage of Population Vaccinated')

    if country == 'Global':

        title = 'COVID VACCINATION DATA FOR THE WORLD MAY 27th, 2021'

    else:

        title = 'COVID VACCINATION DATA FOR ' + country.upper() + ' - MAY 27th, 2021'

    plt.title(title)
    plt.show()


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


if __name__ == '__main__':
    main()