import { useEffect } from "react";
import { useMap } from "react-leaflet";

/**
 * Fixes the Explore Network map sizing/zoom bug.
 *
 * react-leaflet only measures its container once, right when the map is
 * created. On this page the map sits inside a flex/scroll dashboard layout
 * (DashboardLayout > main.overflow-y-auto), so the container's final size
 * isn't always settled at that exact instant — the browser tab becoming
 * active, a font/webfont finishing layout, or the sidebar/topbar reflowing
 * a moment later can all leave Leaflet holding a stale (usually too-small)
 * size. When that happens tiles render offset, the visible map appears
 * cropped or blank in places, and zooming/panning misbehaves because
 * Leaflet is calculating pixel offsets against the wrong container
 * dimensions.
 *
 * The fix is to explicitly tell Leaflet to re-measure (`invalidateSize`)
 * once right after mount, and again any time the container itself resizes
 * (window resize, layout reflow, etc.) via a ResizeObserver.
 */
export default function MapResizeHandler() {
  const map = useMap();

  useEffect(() => {
    // Re-measure on the next frame, after layout has settled.
    const raf = requestAnimationFrame(() => map.invalidateSize());

    const container = map.getContainer();
    const observer = new ResizeObserver(() => {
      map.invalidateSize();
    });
    observer.observe(container);

    return () => {
      cancelAnimationFrame(raf);
      observer.disconnect();
    };
  }, [map]);

  return null;
}
