GTA1 Map Viewer
===============

Small experiment with webgl (and the excellent `three.js`_ framework) that renders
the map from GTA1.


Quickstart
----------

1. Download **Grand Theft Auto 1** from http://www.rockstargames.com/classics/
2. Install the game
3. Copy *NYC.CMP* and *STYLE001.G24* from *GTADATA/* into the *data/* directory.
4. Run *build.py*. (This will extract map data and textures and store them in the *_build/* directory)
5. Run *serve.py*. (Starts a webserver to deliver the files in the *_build/* directory)
6. Open localhost:8000 in your browser


Thanks
------

* DMA Design for GTA (and providing valuable documentation on file formats; "CityScape Data Structure")
* `Corrections to the DMA docs`_ from the GTACars author(s)
* Michael Mendelsohn: `The unofficial Grand Theft Auto Reference Handbook`_
* MasterOfJOKers


.. _`three.js`: https://github.com/mrdoob/three.js
.. _`Corrections to the DMA docs`: http://www.fifengr.com/gtacars/topic.html
.. _`The unofficial Grand Theft Auto Reference Handbook`: http://gta.mendelsohn.de/Reference/index.html
