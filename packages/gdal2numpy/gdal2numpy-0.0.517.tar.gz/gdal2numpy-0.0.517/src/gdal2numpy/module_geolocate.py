# -------------------------------------------------------------------------------
# MIT License:
# Copyright (c) 2012-2022 Luzzi Valerio
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        module_geolocate.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     30/11/2023
# -------------------------------------------------------------------------------

import requests


def geolocate(address, limit=16, provider="photon"):
    """
    geolocate
    """
    if address:
        params = {"q": address}

        if provider == "photon":
            url = f"https://photon.komoot.io/api"
        elif provider == "nominatim":
            url = f"https://nominatim.openstreetmap.org/search"
            params["format"] = "geojson"
        else:
            url = f"https://photon.komoot.io/api"

        if limit:
            params["limit"] = limit

        r = requests.get(url, params=params, timeout=30)

        if r.status_code == 200:
            data = r.json()
            res = []
            if "features" in data:
                for feature in data["features"]:
                    item = feature["properties"]
                    coords = feature["geometry"]["coordinates"]
                    item["lon"] = coords[0]
                    item["lat"] = coords[1]
                    res.append(item)
            else:
                res = data
            return res
    return False


def geolocate_building(address, provider="photon"):
    """
    geolocate_building - filter the result to return only buildings
    """
    items = geolocate(address, limit=10, provider=provider)
    res = []
    for item in items:
        if item["type"] == "house":
            res.append(item)
    return res




if __name__ == '__main__':
    address = "via delle Piante 4, Rimini"
    address = "via Emilia 155, Rimini"
    address = "Piazzale del Popolo, 1, 47923 Rimini RN"
    result = geolocate_building(address, provider="photon")
    print(result)
    print("=====================================")
    result = geolocate_building(address, provider="nominatim")
    print(result)
