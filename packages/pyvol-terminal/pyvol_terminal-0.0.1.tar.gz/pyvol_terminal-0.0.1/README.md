# PyVol Surface

A package that utilises QT and OpenGL graphics to visualise **realtime** 3D volatility surfaces and analytics.

Key Features
-------------
- Realtime plotting
- Can use your own engines for option pricing, interest/divident-rates and interpolation engines (package includes default engines)
- Can use options with a future as the underlying and many different underlyings for the same option's chain.
- Generate the surface's smile and term structure at any point along the surface


Minimum Requirements
--------------------
* numpy==2.2.6
* pandas==2.2.3
* PyOpenGL==3.1.9
* PyOpenGL-accelerate==3.1.9
* pyqtgraph==0.14.0.dev0
* PySide6==6.9.1

Requirements for examples
-------------------------
* nest_asyncio==1.6.0
* numba==0.61.2
* websockets==15.0.1
* Requests==2.32.3
* scipy==1.15.2
* py_vollib_vectorized==0.1.1

