const assert = require('node:assert/strict');

const {
  buildStyleLayerIndex,
  describeFeatureForInspector,
  summarizeProperties
} = require('./inspector');

function createFeature(properties, geometryType = 'Point') {
  return {
    getProperties() {
      return properties;
    },
    getGeometry() {
      return {
        getType() {
          return geometryType;
        }
      };
    }
  };
}

function test(name, fn) {
  try {
    fn();
    console.log('ok - ' + name);
  } catch (error) {
    console.error('not ok - ' + name);
    throw error;
  }
}

test('buildStyleLayerIndex groups Mapbox style layers by source layer', () => {
  const index = buildStyleLayerIndex({
    layers: [
      { id: 'water-fill', type: 'fill', 'source-layer': 'water' },
      { id: 'water-label', type: 'symbol', 'source-layer': 'water' },
      { id: 'road-line', type: 'line', 'source-layer': 'transportation' }
    ]
  });

  assert.deepEqual(index.water, [
    { id: 'water-fill', type: 'fill' },
    { id: 'water-label', type: 'symbol' }
  ]);
  assert.deepEqual(index.transportation, [
    { id: 'road-line', type: 'line' }
  ]);
});

test('describeFeatureForInspector exposes category, geometry, style layers, and properties', () => {
  const feature = createFeature({
    layer: 'transportation',
    class: 'primary',
    name: 'Narva mnt',
    geometry: 'internal value'
  }, 'LineString');

  const description = describeFeatureForInspector(feature, {
    transportation: [
      { id: 'road-primary', type: 'line' },
      { id: 'road-label', type: 'symbol' }
    ]
  });

  assert.equal(description.category, 'transportation');
  assert.equal(description.geometryType, 'LineString');
  assert.deepEqual(description.styleLayers, [
    { id: 'road-primary', type: 'line' },
    { id: 'road-label', type: 'symbol' }
  ]);
  assert.deepEqual(description.properties, [
    ['class', 'primary'],
    ['name', 'Narva mnt']
  ]);
});

test('describeFeatureForInspector reads geometry type from OpenLayers render features', () => {
  const feature = {
    getProperties() {
      return { layer: 'water', class: 'lake' };
    },
    getType() {
      return 'Polygon';
    }
  };

  const description = describeFeatureForInspector(feature, {});

  assert.equal(description.geometryType, 'Polygon');
});

test('summarizeProperties prefers useful scalar values and skips noisy internals', () => {
  const summary = summarizeProperties({
    layer: 'place',
    name: 'Tallinn',
    population: 461000,
    geometry: {},
    metadata: { nested: true },
    empty: ''
  });

  assert.deepEqual(summary, [
    ['name', 'Tallinn'],
    ['population', '461000']
  ]);
});
