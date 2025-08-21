import { render_slides } from './plixlab.js';

document.addEventListener('DOMContentLoaded', function () {
  const PLIXLAB_PORT = window.PLIXLAB_PORT || 8889;
  const HOT_RELOAD = window.PLIXLAB_HOT_RELOAD ?? true;

  function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
  }

  function setupSSE() {
    const eventSource = new EventSource(`http://localhost:${PLIXLAB_PORT}/events`);

    eventSource.onmessage = (event) => {
      if (event.data === "ready") {
        connectWebSocket();
      }
    };
  }

  function connectWebSocket() {
    const ws = new WebSocket(`ws://localhost:${PLIXLAB_PORT}/data`);
    ws.binaryType = "arraybuffer";

    ws.onmessage = (event) => {
      const unpackedData = msgpack.decode(new Uint8Array(event.data));
      render_slides(unpackedData);
    };
  }
function fetchStatic() {
  fetch(`http://localhost:${PLIXLAB_PORT}/static_data`)
    .then((res) => res.arrayBuffer())
    .then((buf) => {
      const unpackedData = msgpack.decode(new Uint8Array(buf));
      render_slides(unpackedData);

      // Gracefully shut down the backend
      fetch(`http://localhost:${PLIXLAB_PORT}/shutdown`, {
        method: "POST"
      });
    });
}

  const suppressSSE = getUrlParameter('suppress_SSE') === 'true';

  if (HOT_RELOAD && !suppressSSE) {
    setupSSE();
  } else {
    console.log("Hot reload is off — loading static data");
    fetchStatic();
  }
});
