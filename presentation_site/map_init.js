document.addEventListener('DOMContentLoaded', function () {
    // Initialize the map centered on California
    const map = L.map('map').setView([37.0, -120.0], 6);

    // Add OpenStreetMap tiles (Dark mode style if possible, but standard is fine. User likes "Premium", so maybe a dark tile layer?)
    // Using CartoDB Dark Matter for a "premium" feel that matches the dark theme likely implied by "Wildfire Intelligence"
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19,
        detectRetina: true
    }).addTo(map);

    // Define icons
    const createIcon = (color) => {
        return L.divIcon({
            className: 'custom-div-icon',
            html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 20px ${color};"></div>`,
            iconSize: [30, 30],
            iconAnchor: [15, 15],
            popupAnchor: [0, -15]
        });
    };

    // Parse data and add markers
    wildfireData.forEach(item => {
        let color = '#34c759'; // Default Green (Stable)
        const status = item.status ? item.status.toLowerCase() : '';

        // Color coding based on Monday.com board status
        if (status.includes('act')) {
            color = '#ff3b30'; // Red
        } else if (status.includes('watch')) {
            color = '#ffcc00'; // Yellow
        } else if (status.includes('monitor')) {
            color = '#007aff'; // Blue
        } else if (status.includes('stable')) {
            color = '#34c759'; // Green
        }

        // Use coordinates or default
        const coords = item.coords;

        if (coords) {
            const marker = L.marker(coords, { icon: createIcon(color) }).addTo(map);

            // Build popup content
            const popupContent = `
                <div style="font-family: 'Inter', sans-serif; min-width: 200px;">
                    <h3 style="margin: 0 0 5px 0; color: #333;">${item.name}</h3>
                    <div style="margin-bottom: 5px;">
                        <span style="background: ${color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; font-weight: 600;">${item.status}</span>
                        <span style="font-size: 0.8em; color: #666; margin-left: 5px;">Mag: ${item.magnitude}</span>
                    </div>
                    <p style="margin: 0; font-size: 0.9em; color: #555;">${item.description ? item.description.substring(0, 100) + '...' : ''}</p>
                </div>
            `;

            marker.bindPopup(popupContent, { closeButton: false }); // Hide close button for hover effect

            marker.on('mouseover', function (e) {
                this.openPopup();
            });

            marker.on('mouseout', function (e) {
                this.closePopup();
            });
        }
    });

    // Fix map sizing issues that sometimes happen with dynamic loading
    setTimeout(() => { map.invalidateSize(); }, 100);
});
