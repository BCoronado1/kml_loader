from typing import Dict

import matplotlib.pyplot as plt
import shapely

from util import load_kml, Shape

if __name__ == '__main__':
    # KML file downloaded from
    # https://developers.google.com/kml/documentation/kml_tut
    kml_file = "./KML_Samples.kml"
    shapes: Dict[str, Shape] = load_kml(kml_file=kml_file)
    for k, v in shapes.items():
        print(f"id: {k} name: {v.name} wkt: {v.shape.wkt}")

    pentagon = shapes["thepentagon"].shape
    p_json = shapely.to_geojson(pentagon)
    print("Pentagon json")
    print(p_json)

    print("Pentagon wkt")
    print(pentagon.wkt)

    print("Plot Pentagon")
    x, y = pentagon.exterior.xy
    plt.plot(x, y)
    plt.show()
