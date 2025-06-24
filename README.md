# TransientXplorer
This tool provides a web application portal to monitor candidate profiles of TransientX blind and targeted single pulse searches.

## Running TransientXplorer:
The application is embedded into a docker container. First clone the application to a local directory:
$ git clone https://gitlab.mpcdf.mpg.de/pral/TransXplorer

Once you initialise the docker container, the application can be run using:
$ python3 TransientXplorer.py

This will open a portal to localhost:8050 which you can parse from your local web browser.



Make a directory `\utils' within the directory where you cloned the tool. 

Run TransientX (Men & Barr 2024) such that the output PNG files and candidate csv file are written to `\utils'. 

Open the web interface and select the relevant candidate file from the drop-down menu. This will create a monitoring table and graph.
You can interactivele select which parameters you want to visualize from the drop-down selectors.

The web interface dynamically updates as the transientX search proceeds. The refresh rate can be modified to user-specific values through the refresh interval selector






