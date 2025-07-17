# TransientXplorer

A lightweight Dash web application for exploring transient candidates interactively using image data and associated metadata. Ideal for radio astronomy burst candidates or similar time-domain datasets.

---

##  Features

- Interactive visualization of burst candidates  
- Filter and explore events by temporal widths, arrival times, or other parameters  
- Responsive web UI powered by Plotly Dash  
- Dockerized for easy deployment and portability  

---


### 1. Clone this repository

```bash
git clone https://gitlab.mpcdf.mpg.de/pral/TransientXplorer.git
cd TransientXplorer
```
##  Run with Singularity (No Docker or root access needed)

You can run the app using a pre-built Singularity image.

### Step 1: Download the `.sif` file

Download the latest `.sif` from Zenodo:

[Download transientXplorer.sif from Zenodo](https://zenodo.org/records/15974012/files/transientxplorer.sif?download=1)  

To Download it from the terminal:
```
wget -O transientxplorer.sif "https://zenodo.org/records/15974012/files/transientxplorer.sif?download=1"
```


DOI: [10.5281/zenodo.15974011](https://doi.org/10.5281/zenodo.15974011)


###  Step 2: Run the app

Make sure you have your candidate data (e.g., CSV and images) in a folder like `./candidates`, then run:

```bash
singularity exec --bind ./candidates:/data transientxplorer.sif python3 TransientXplorer.py
```
## Known Bugs:
By default, the app runs on ```port 8050``` which might be already in use on certain servers. If this is the case, change the port number in the ```TransientXplorer.py``` script. 

To check which ports are already in use on your device, run:
```
netstat -tuln
```

## Web Interface Overview
![Web_Interface](examples/web_interface.png)

##  Panel Breakdown

###  Left Panel (Controls)

- **Select CSV file**: Choose a `.cands` file from the dropdown list (Note: The application only accepts .csv or .cands files)
- **X/Y Axis**: Select which variables to display on the X and Y axes (e.g., `MJD`, `Burst_DM`, etc.)
- **Scale**: Toggle between `linear` and `log` scale for each axis
- **Auto Refresh**: Enable to refresh the data view automatically every N seconds

###  Right Panel (Visualization)

- **Scatter Plot**: (Default)
    - **X-axis**: MJD
    - **Y-axis**: Dispersion Measure (pc cm⁻³)
    - **Color**: Width (ms)
    - **Size**: S/N (Signal-to-Noise Ratio)
- Click any point to open the associated candidate image
- **Histogram**: Shows the distribution of the Y-axis quantity

- **Tabular Data**:
    - Shows the burst properties mentioned above and the TransientX PNG files
    
    - User can click on any tabular cell to open the associated candidate image

### Additional features:
- The margin between graph and table can be dragged to resize the layout according to your needs.
- The scatter plot can be filtered by applying filters on different burst properties
    - For example: Only visualize high S/N ratio candidates using a (> 30) filter in the S/N column





## Citation:
If you use TransientXplorer in your work, please cite the Zenodo DOI:
```
@misc{transientxplorer_zenodo,
  author       = {Your Name(s)},
  title        = {TransientXplorer: A lightweight Dash app for transient candidate exploration},
  year         = {2025},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.15974011},
  url          = {https://doi.org/10.5281/zenodo.15974011}
}
```

##  Contact

For questions, bugs, or feature requests, open an issue or contact:  
limaye@mpifr-bonn.mpg.de






