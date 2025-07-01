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
git clone https://github.com/your-username/TransientXplorer.git
cd TransientXplorer
```
### 2. Build Docker Image
```docker build -t transientxplorer .  (You only need to do this once)```

  

### 3. Run the container:
```
docker run -it \
  -v /home/user/Desktop/test_cands:/data \
  -p 8050:8050 \
  transientxplorer \
  python3 /workspace/TransientXplorer.py 
  ```

### Directory Structure (Inside Container):
```
/workspace/
  ├── TransientXplorer.py         # Main Dash app
  ├── utils/                      # Helper scripts (optional)
  ├── requirements.txt
  └── ...
/data/
  └── [mounted image directory from host]
  ```


For questions, bugs, or feature requests, open an issue or contact [limaye@mpifr-bonn.mpg.de].







