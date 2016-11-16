import csv, json, re
from geonamescache import GeonamesCache
from loclists import check_unresolved
from os import path

BASE_URL = "data/"
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


def determine_country(locstr):
    """Try to determine country from given location string."""

    locstr = re.sub(re_ws, ' ', re.sub(re_ignore, ' ', locstr)).strip()

    if locstr in countries_by_locstr:
        return countries_by_locstr[locstr]

    # try different split chars
    for sc in [',', '/', '-', ' ', ':', '#', '->', '\\']:
        splitted = locstr.split(sc)
        splitted.reverse()
        country = test_locs(splitted)
        if country is not None:
            countries_by_locstr[locstr] = country
            return country

    # check manually resolved locations
    country = check_unresolved(locstr.lower())
    if country is not None:
        countries_by_locstr[locstr] = country
        return country


def parse_users_from_csv(filename='users.csv'):
    """Parse user locations in CSV format: 'user, location'"""
    with open(path.join(BASE_URL, filename), 'r') as fcsv:
        reader = csv.reader(fcsv)
        next(reader)
        countrymap = []
        unresolved = {}
        amount = 0
        incorrect = 0
        for record in reader:
            amount += 1
            user, location = record
            country = determine_country(location)
            if country is not None:
                countrymap.append((user, country))
            else:
                incorrect += 1
                if location not in unresolved:
                    unresolved[location] = 1
                else:
                    unresolved[location] += 1

    # print statistics of results
    print("Percentage of unresolved locations=", incorrect / amount)

    # write output file
    wcsv = open(path.join(BASE_URL, 'users_to_countries.csv'), 'w')
    writer = csv.writer(wcsv, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['User', 'Country'])
    for c in countrymap:
        writer.writerow([c[0], c[1]])
    wcsv.close()

    # write the locations we could not parse
    uf = open(path.join(BASE_URL, 'unresolved_locations.txt'), 'w')
    for l, c in sorted(unresolved.items(), key=lambda x: x[1]):
        uf.write('{} -> {}\n'.format(l, c))
    uf.close()


def parse_gh_users(fileurl):
    """Parse GitHub user json data."""
    # file where we write the output
    wcsv = open(path.join(BASE_URL, 'gh_users.csv'), 'w')
    writer = csv.writer(wcsv, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["ID","Login","Joined","Location","Email","Avatar","GravatarId","Name","Company","Blog","Hireable","Bio","Public repos","Public gists","Followers","Following"])

    # open input json file
    with open(fileurl) as data_file:    
        data = json.load(data_file)
        unresolved = {}
        parsed = 0
        incorrect = 0
        for user in data:
            location = user['location']
            if location is not None:
                country = determine_country(location)
                if country is not None:
                    parsed += 1
                    writer.writerow([user['id'], user['login'], user['created_at'], country, user['email'],
                        user['avatar_url'], user['gravatar_id'], user['name'], user['company'], user['blog'], user['hireable'], 
                        user['bio'], user['public_repos'], user['public_gists'], user['followers'], user['following']])
                    continue
                else:
                    incorrect += 1
                    if location not in unresolved:
                        unresolved[location] = 1
                    else:
                        unresolved[location] += 1

            # if the country could not be parsed, write an empty location
            writer.writerow([user['id'], user['login'], user['created_at'], '', user['email'], 
                        user['avatar_url'], user['gravatar_id'], user['name'], user['company'], user['blog'], user['hireable'], 
                        user['bio'], user['public_repos'], user['public_gists'], user['followers'], user['following']])
        # print statistics of results
        print("Parsed {} from {} ({}%) of {} total users".format(parsed, incorrect + parsed, parsed / (incorrect + parsed), len(data)))
    wcsv.close()

    # write the locations we could not parse
    uf = open(path.join(BASE_URL, 'unresolved_locations_top.txt'), 'w')
    for l, c in sorted(unresolved.items(), key=lambda x: x[1]):
        uf.write('{} -> {}\n'.format(l, c))
    uf.close()
