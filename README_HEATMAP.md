# Wildfire Heatmap Deployment Guide

This repository contains an interactive Wildfire Heatmap for California with a time-controlled slider.

## How to Deploy to GitHub Pages

1. **Create a GitHub Repository**:
   - Go to [GitHub](https://github.com/new) and create a new repository (e.g., `wildfire-heatmap`).

2. **Upload the Files**:
   - Push the generated `index.html` to the root of your repository.
   - You can also include `generate_heatmap.py` and `config.py` if you want to keep the source code there.

3. **Enable GitHub Pages**:
   - In your GitHub repository, go to **Settings** > **Pages**.
   - Under **Build and deployment**, set the **Source** to "Deploy from a branch".
   - Select the `main` branch and the `/ (root)` folder.
   - Click **Save**.

4. **View Your Map**:
   - After a few minutes, your map will be live at `https://<your-username>.github.io/<repo-name>/`.

## Features
- **Time Slider**: Manually control the date to see fire progression.
- **Heat Intensity**: Colors intensify based on the volume of reports in a specific area.
- **Zoomable**: Interactive map powered by Folium.
