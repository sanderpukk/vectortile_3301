const assert = require('node:assert/strict');
const fs = require('node:fs');

function test(name, fn) {
  try {
    fn();
    console.log('ok - ' + name);
  } catch (error) {
    console.error('not ok - ' + name);
    throw error;
  }
}

test('docker viewer serves the inspector helper referenced by index.html', () => {
  const indexHtml = fs.readFileSync('C:/vectortile/python-pipeline/viewer/index.html', 'utf8');
  const dockerCompose = fs.readFileSync('C:/vectortile/python-pipeline/docker-compose.yml', 'utf8');

  assert.match(indexHtml, /<script src="\/inspector\.js"><\/script>/);
  assert.match(
    dockerCompose,
    /\.\/viewer\/inspector\.js:\/usr\/share\/nginx\/html\/inspector\.js:ro/
  );
});
