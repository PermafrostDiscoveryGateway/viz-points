# viz-points
Python package for post-processing point-cloud data for 3D visualization

## Repository contents

- [notebooks/](notebooks/) contains the simplified and annotated Jupyter Notebook version of the LiDAR processing workflow
- [pdgpoints/](pdgpoints/) contains the application code comprising the library

## Installation

Requirements:
- [py3dtiles](https://gitlab.com/oslandia/py3dtiles) (Oslandia or [PDG version](https://github.com/PermafrostDiscoveryGateway/py3dtiles))
- rapidlasso [las2las](https://rapidlasso.com/lastools/las2las/) post-November 2022 (rapidlasso [precompiled Windows](https://github.com/LAStools/LAStools/blob/master/README.md#links) or included [linux binary](https://rapidlasso.de/release-of-lastoolslinux/))

Visualization requirements:
- A tool that can display 3dtiles data, such as [Cesium](https://cesium.com)

### Visualizing the data in Cesium

You can view the output tiles in a Cesium environment. For steps for how to visualize the tiles with a local Cesium instance, see the [documentation here in pdg-info](https://github.com/julietcohen/pdg-info/blob/main/05_displaying-the-tiles.md#option-1-run-cesium-locally).

![Test dataset](pdgpoints/testdata/lp.png)

More info on the above test dataset [here](pdgpoints/testdata/README.md).

Below is an example of the `cesium.js` file that will display a 3dtiles tileset at `./3dtiles/tileset.json` (you will need your own access token):


```javascript

function start(){// Your access token can be found at: https://cesium.com/ion/tokens.

  Cesium.Ion.defaultAccessToken = "YOUR-TOKEN-HERE"

  const viewer = new Cesium.Viewer('cesiumContainer');

  const imageryLayers = viewer.imageryLayers;

  var tileset = new Cesium.Cesium3DTileset({
    url: "3dtiles/tileset.json",
    debugShowBoundingVolume: true,
    debugShowContentBoundingVolume: false,
    debugShowGeometricError: false,
    debugWireframe: true
  });

  viewer.scene.primitives.add(tileset);

  window.zoom_to_me = function(){
    viewer.zoomTo(tileset);
  }

  tileset.readyPromise.then(zoom_to_me).otherwise(error => { console.log(error) });
}

start()
```