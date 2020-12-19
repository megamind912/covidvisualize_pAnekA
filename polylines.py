import requests
import flexpolyline as fp


def find_line(mode, origin, destination):
    origin = ','.join(reversed(origin.split(',')))
    print(origin)
    destination = ','.join(reversed(destination.split(',')))
    print(destination)
    apikey = 'UFxVXR8hvIufas9Ea3xQPcIE86T68lQm4VpBHI68f-E'
    url = f"https://router.hereapi.com/v8/routes?transportMode={mode}&origin={origin}&destination={destination}&return=polyline&apikey={apikey}"
    print(url)
    response = requests.get(url)
    data = response.json()
    # print(data)
    # print(data['routes'][0]['sections'][0]['polyline'])
    coordinates = fp.decode(data['routes'][0]['sections'][0]['polyline'])
    # print(coordinates)
    coordinates = list(map(tuple, map(reversed, coordinates)))
    print(coordinates)
    return coordinates


if __name__ == '__main__':
    find_line('car', '52.619438,39.573161', '52.605931,39.577094')
