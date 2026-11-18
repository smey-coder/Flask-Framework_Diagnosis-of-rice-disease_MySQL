document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".field-boundary-map").forEach(function (container) {
    try {
      const geometry = JSON.parse(container.dataset.boundary);
      const map = L.map(container, {
        zoomControl: false,
        scrollWheelZoom: false,
        dragging: false,
        doubleClickZoom: false,
        keyboard: false,
        touchZoom: false
      });

      L.tileLayer("https://{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", {
        maxZoom: 20,
        subdomains: ["mt0", "mt1", "mt2", "mt3"],
        attribution: "&copy; Google Maps"
      }).addTo(map);

      const boundary = L.geoJSON(geometry, {
        style: { color: "#22c55e", weight: 3, fillColor: "#22c55e", fillOpacity: 0.3 }
      }).addTo(map);
      map.fitBounds(boundary.getBounds(), { padding: [6, 6] });
    } catch (error) {
      console.error("Field boundary map could not be loaded.", error);
      container.textContent = "Map preview unavailable.";
    }
  });
});
