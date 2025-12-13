declare module 'leaflet.markercluster' {
  import * as L from 'leaflet'

  namespace MarkerClusterGroup {
    interface Options extends L.LayerOptions {
      maxClusterRadius?: number
      iconCreateFunction?: (cluster: MarkerClusterGroup) => L.Icon | L.DivIcon
      spiderfyOnMaxZoom?: boolean
      showCoverageOnHover?: boolean
      zoomToBoundsOnClick?: boolean
      singleMarkerMode?: boolean
      disableClusteringAtZoom?: number
      removeOutsideVisibleBounds?: boolean
      animate?: boolean
      animateAddingMarkers?: boolean
      disableDefaultIcon?: boolean
      chunkedLoading?: boolean
      chunkInterval?: number
      chunkDelay?: number
      chunkProgress?: (processed: number, total: number, elapsed: number) => void
    }
  }

  class MarkerClusterGroup extends L.LayerGroup {
    constructor(options?: MarkerClusterGroup.Options)
    addLayers(layers: L.Marker[]): void
    removeLayers(layers: L.Marker[]): void
    clearLayers(): void
    refreshClusters(): void
    getVisibleParent(marker: L.Marker): L.Marker | MarkerClusterGroup
    hasLayer(layer: L.Marker): boolean
    zoomToShowLayer(layer: L.Marker, callback?: () => void): void
  }

  export = MarkerClusterGroup
}


