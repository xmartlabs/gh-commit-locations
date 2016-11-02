import csv, json, re
from geonamescache import GeonamesCache
from loclists import check_unresolved


countries_by_locstr = {}
gc = GeonamesCache()
countries = gc.get_countries()
countries_by_names = gc.get_countries_by_names()
us_states = gc.get_us_states()
us_states_by_names = gc.get_us_states_by_names()

re_ignore = re.compile(r'[\.\(\)\d-]')
re_ws = re.compile(r'\s{2,}')

def test_locs(locs):
    for loc in locs:
        loc = loc.strip().lower()
        loctitle = loc.title()
        locupper = loc.upper()
        if loc in countries_by_names:
            return loc
        elif loctitle in countries_by_names:
            return loctitle
        elif 2 == len(loc) and locupper in us_states:
            return 'United States'
        elif loc in us_states_by_names or loctitle in us_states_by_names:
            return 'United States'
        elif locupper in ['USA', 'US']:
            return 'United States'
        elif locupper in ['GB', 'UK']:
            return 'United Kingdom'
        elif locupper in countries:
            return countries[locupper]['name']
        elif locupper in countries:
            return countries[locupper]['name']
        else:
            for ll in [loc, loctitle]:
                cities = gc.get_cities_by_name(ll)
                # unique city names
                lencities = len(cities)
                if 1 == lencities:
                    return countries[list(cities[0].values())[0]['countrycode']]['name']
                # assume the largest city
                elif lencities > 1:
                    largestcity = sorted([(city['population'], city['countrycode']) for cdict in cities for gid, city in cdict.items()])[-1]
                    return countries[largestcity[-1]]['name']


def determine_country(locstr, langcnt):
    """Try to determine country from given location string."""

    locstr = re.sub(re_ws, ' ', re.sub(re_ignore, ' ', locstr)).strip()

    if locstr in countries_by_locstr:
        return countries_by_locstr[locstr]

    # try different split chars
    for sc in [',', '/', '-', ' ', ':', '#', '->']:
        splitted = locstr.split(sc)
        splitted.reverse()
        print(splitted)
        country = test_locs(splitted)
        if country is not None:
            countries_by_locstr[locstr] = country
            return country

    # check manually resolved locations
    country = check_unresolved(locstr.lower())
    if country is not None:
        countries_by_locstr[locstr] = country
        return country

    unresolved_locations.append('%s, %d' % (locstr, langcnt))
