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

![Web_Interface](examples/web_interface.png)


## 📬 Contact

For questions, bugs, or feature requests, open an issue or contact:  
📧 limaye@mpifr-bonn.mpg.de






