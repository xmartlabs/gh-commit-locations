import csv, json, re
from geonamescache import GeonamesCache

def export_country_table(fileurl):
	gc = GeonamesCache()
	countries = gc.get_countries()
	with open(fileurl, 'w') as file:
		writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
		writer.writerow(['name', 'iso', 'population', 'continentcode', 'areakm2'])
		for k, value in countries.items():
			writer.writerow([value['name'], k, int(value['population']), value['continentcode'], value['areakm2']])