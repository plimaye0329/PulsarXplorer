# TransientXplorer

A lightweight Dash web application for exploring transient candidates interactively using image data and associated metadata. Ideal for radio astronomy burst candidates or similar time-domain datasets.

---

## 🚀 Features

- Interactive visualization of burst candidates  
- Filter and explore events by band, time, or other parameters  
- Responsive web UI powered by Plotly Dash  
- Dockerized for easy deployment and portability  

---


### 1. Clone this repository

```bash
git clone https://gitlab.mpcdf.mpg.de/pral/TransientXplorer.git
cd TransientXplorer
```

##  Run via Singularity

If you do not have Docker or root access, you can use Singularity. A `transientxplorer.sif` file is included in the cloned repository.

```bash
singularity exec --bind /home/candidates:/data transientxplorer.sif python3 TransientXplorer.py
```

Make sure to replace `/home/candidates` with the actual path to your data directory. The application will serve on **http://localhost:8050**

---

## Web Interface Overview
![Web_Interface](examples/web_interface.png)

## 🧭 Panel Breakdown

### 🧾 Left Panel (Controls)

- **Select CSV file**: Choose a `.cands` file from the dropdown list
- **X/Y Axis**: Select which variables to display on the X and Y axes (e.g., `MJD`, `Burst_DM`, etc.)
- **Scale**: Toggle between `linear` and `log` scale for each axis
- **Auto Refresh**: Enable to refresh the data view automatically every N seconds

### 🧾 Rigth Panel (Visualization)

- **Scatter Plot**: (Default)
    - **X-axis**: MJD
    - **Y-axis**: Dispersion Measure (pc cm^{-3})
    - **Color**: Width (ms)
    - **Size**: S/N (Signal-to-Noise Ratio)
- Click any point to open the associated candidate image
- Histogram: Shows the distribution of the Y-axis quantity




## 📬 Contact

For questions, bugs, or feature requests, open an issue or contact:  
📧 limaye@mpifr-bonn.mpg.de






