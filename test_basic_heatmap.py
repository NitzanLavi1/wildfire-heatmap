import folium
from folium.plugins import HeatMapWithTime

data = [[[37, -120, 1], [37.1, -120.1, 0.8]], [[37.2, -120.2, 0.5]]]
index = ['2025-01-01', '2025-01-02']
m = folium.Map(location=[37, -120], zoom_start=6)
HeatMapWithTime(data, index=index).add_to(m)
m.save('test_basic.html')
print("Saved test_basic.html")
