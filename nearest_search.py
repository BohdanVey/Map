import folium
from geopy.geocoders import Nominatim
from math import sin, cos, sqrt, atan2, radians


def get_distance(lat1, lng1, lat2, lng2):
    '''
    (float,float,float,float) -> float
    Return distance between two points
    '''
    R = 6300
    lat1 = radians(lat1)
    lng1 = radians(lng1)
    lat2 = radians(lat2)
    lng2 = radians(lng2)
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = (sin(dlat / 2)) ** 2 + cos(lat1) * cos(lat2) * (sin(dlng / 2)) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance


def get_cities(src, year):
    '''
    (src,year) -> list
    Get coordinates of all films location at this year
    '''
    f = open(src, errors='ignore', encoding='UTF-8')
    i = 0
    cities = {}
    for line in f.readlines():
        if i == 0 and line[0] != '=':
            continue
        i = 1
        if line[0] == '=':
            continue
        j = 1
        try:
            if line.split('(')[1][:4] == str(year):
                line = line.split('	')
                cities[line[-1][:-1]] = cities.get(line[-1], [])
                cities[line[-1][:-1]].append(line[0])
        except:
            pass
    f.close()
    return cities


top_10_nearest = []
limit = 400
used_coordinates = set()


def get_nearest_cities(lat, lng, cities):
    '''
    (float,float,list) -> list
    Get nearest points to our coodinatest
    '''
    global top_10_nearest
    global limit
    geolocator = Nominatim(user_agent="program", timeout=2)
    for city2 in cities:
        if limit % 10 == 0:
            print(limit)
        if limit < 0:
            break
        try:
            place = city2.strip()
            limit -= 1
            location = geolocator.geocode(place)
            lat2, lng2 = location.latitude, location.longitude
            if (lat2, lng2) in used_coordinates:
                continue
            used_coordinates.add((lat2, lng2))
            top_10_nearest.append(
                [get_distance(lat, lng, lat2, lng2), place, lat2, lng2])
        except:
            pass


lat, lng = 0, 0


def check_countries(country, city2):
    '''
    (str,str) -> bool
    Check are points in same country?
    >>> check_countries('England','Bradford, West Yorkshire, England, UK')
    True
    '''
    if country in city2:
        return True


def read_location(src):
    '''
    str->None
    Main program
    '''
    i = 0
    year = int(input('Print a year: '))
    cities = get_cities(src, year)
    global lat, lng
    lat, lng = [float(x) for x in input('Print a coordinates: ').split()]
    coordinates = str(lat) + ', ' + str(lng)
    city, country = '', ''
    try:
        locator = Nominatim(user_agent='myGeocoder')
        location = locator.reverse(coordinates).raw
        city, country = location['address']['city'], location['address']['country']
    except:
        city, country = 'Text you can`t find', 'Text you can`t find'
    cities2 = set()
    countries = set()

    for city2 in cities:
        if city in city2:
            cities2.add(city2)
        elif check_countries(country, city2):
            countries.add(city2)
        else:
            try:
                if location['address']['state'] in city2:
                    countries.add(city2)
            except:
                pass
    get_nearest_cities(lat, lng, cities2)
    if len(top_10_nearest) >= 10:
        return
    get_nearest_cities(lat, lng, countries)
    if len(top_10_nearest) >= 10:
        return
    get_nearest_cities(lat, lng, cities)


def print_map(top_10_nearest):
    '''
    list->map
    Return map
    '''
    colors = ['blue', 'red', 'green', 'purple',
              'black', 'yellow', 'orange', 'gold', 'white']
    max_dist = top_10_nearest[9][0]
    zooms = 0
    while 64 * max_dist / 400 * (2 ** zooms) < 4000:
        zooms += 1
    m = folium.Map(location=[lat, lng], zoom_start=zooms)
    layer2 = folium.FeatureGroup(name="Nearest map")
    layer3 = folium.FeatureGroup(name="Capital map")

    for nearest in top_10_nearest:
        lt, ln = nearest[2], nearest[3]
        layer2.add_child(folium.Marker(location=[lt, ln],
                                       popup=nearest[1],
                                       icon=folium.Icon()))
    layer2.add_child(folium.Marker(location=[lat, lng],
                                   popup='Point',
                                   icon=folium.Icon(color='orange')))
    f = open('countries.txt')
    for line in f.readlines():
        line = line.split('	')
        layer3.add_child(folium.Marker(
            location=[float(line[2]), float(line[3])],
            popup=line[0] + ' ' + line[1],
            icon=folium.Icon(color='red')
        ))
    m.add_child(layer2)
    check = input('Print Yes if you want to see all countries capital: ')
    if check.lower() == 'yes':
        m.add_child(layer3)

    m.save('index.html')


coordinates = read_location('locations.list')
top_10_nearest.sort()
top_10_nearest = top_10_nearest[:10]
print_map(top_10_nearest)
