(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
  }
  root.VectorTileInspector = api;
})(typeof window !== 'undefined' ? window : globalThis, function() {
  const SOURCE_LAYER_KEYS = ['layer', 'sourceLayer', 'source_layer', '_layer'];
  const SKIPPED_PROPERTY_KEYS = new Set(['geometry', 'layer', 'sourceLayer', 'source_layer', '_layer']);
  const MAX_STYLE_LAYERS = 8;
  const MAX_PROPERTIES = 8;

  function buildStyleLayerIndex(style) {
    const index = {};
    const layers = style && Array.isArray(style.layers) ? style.layers : [];

    layers.forEach((layer) => {
      const sourceLayer = layer && layer['source-layer'];
      if (!sourceLayer) return;

      if (!index[sourceLayer]) index[sourceLayer] = [];
      index[sourceLayer].push({
        id: layer.id || '(unnamed)',
        type: layer.type || 'unknown'
      });
    });

    return index;
  }

  function summarizeProperties(properties) {
    if (!properties || typeof properties !== 'object') return [];

    return Object.entries(properties)
      .filter(([key, value]) => {
        if (SKIPPED_PROPERTY_KEYS.has(key)) return false;
        if (value === null || value === undefined || value === '') return false;
        return ['string', 'number', 'boolean'].includes(typeof value);
      })
      .slice(0, MAX_PROPERTIES)
      .map(([key, value]) => [key, String(value)]);
  }

  function getFeatureSourceLayer(feature, properties) {
    for (const key of SOURCE_LAYER_KEYS) {
      if (properties && properties[key]) return String(properties[key]);
      if (feature && typeof feature.get === 'function') {
        const value = feature.get(key);
        if (value) return String(value);
      }
    }
    return 'unknown';
  }

  function getFeatureGeometryType(feature) {
    if (!feature) return 'unknown';
    if (typeof feature.getGeometry === 'function') {
      const geometry = feature.getGeometry();
      if (geometry && typeof geometry.getType === 'function') return geometry.getType();
    }
    if (typeof feature.getType === 'function') return feature.getType();
    return 'unknown';
  }

  function describeFeatureForInspector(feature, styleLayerIndex) {
    const properties = feature && typeof feature.getProperties === 'function'
      ? feature.getProperties()
      : {};
    const category = getFeatureSourceLayer(feature, properties);
    const styleLayers = (styleLayerIndex && styleLayerIndex[category] ? styleLayerIndex[category] : [])
      .slice(0, MAX_STYLE_LAYERS);

    return {
      category,
      geometryType: getFeatureGeometryType(feature),
      styleLayers,
      properties: summarizeProperties(properties)
    };
  }

  return {
    buildStyleLayerIndex,
    describeFeatureForInspector,
    summarizeProperties
  };
});
