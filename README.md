# TransientXplorer

A lightweight Dash web application for exploring transient candidates interactively using image data and associated metadata. Ideal for radio astronomy burst candidates or similar time-domain datasets.

---

## 🚀 Features

- Interactive visualization of burst candidates  
- Filter and explore events by band, time, or other parameters  
- Responsive web UI powered by Plotly Dash  
- Dockerized for easy deployment and portability  

---

## 🐳 Run via Docker

### 1. Clone this repository

```bash
git clone https://gitlab.mpcdf.mpg.de/pral/TransientXplorer.git
cd TransientXplorer
```

### 2. Build Docker Image

```bash
docker build -t transientxplorer .
```

### 3. Run the container

```bash
docker run -it \
  -v /home/user/Desktop/MPIfR/utils:/data \
  -p 8050:8050 \
  transientxplorer \
  python3 /workspace/TransientXplorer.py
```

Here:  
- `/home/user/Desktop/MPIfR/utils` is the path where your images and candidate files reside.  
- `/data` is the directory within the container from where the app parses the data to visualize.  

After running the container, open your browser and go to:  
**http://localhost:8050**

---

##  Run via Singularity

If you do not have Docker or root access, you can use Singularity. A `transientxplorer.sif` file is included in the cloned repository.

```bash
singularity exec --bind /home/candidates:/data transientxplorer.sif python3 TransientXplorer.py
```

Make sure to replace `/home/candidates` with the actual path to your data directory. The application will serve on **http://localhost:8050**

---

## 📬 Contact

For questions, bugs, or feature requests, open an issue or contact:  
📧 limaye@mpifr-bonn.mpg.de







