import { render_slides } from './plixlab.js';

document.addEventListener('DOMContentLoaded', async function () {
  const container = document.getElementById('slide-container');

  function getPlxPathFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('file') || 'data.plx';
  }

  const plxPath = getPlxPathFromURL();

  try {
    const response = await fetch(plxPath);
    if (!response.ok) throw new Error(`${plxPath} not found`);

    const buffer = await response.arrayBuffer();
    const unpackedData = msgpack.decode(new Uint8Array(buffer));

    if (container) {
      render_slides(unpackedData, container);
    } else {
      console.error('Slide container not found in index.html.');
    }
  } catch (err) {
    console.error(`Failed to load ${plxPath}:`, err);
  }
});
       
