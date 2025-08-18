// Minimal streamlit messaging shim
function sendMessageToStreamlitClient(type, data) {
  const out = Object.assign({ isStreamlitMessage: true, type }, data);
  window.parent.postMessage(out, "*");
}
const Streamlit = {
  setComponentReady() { sendMessageToStreamlitClient("streamlit:componentReady", { apiVersion: 1 }); },
  setFrameHeight(h) { sendMessageToStreamlitClient("streamlit:setFrameHeight", { height: h }); },
  setComponentValue(v) { sendMessageToStreamlitClient("streamlit:setComponentValue", { value: v }); },
  RENDER_EVENT: "streamlit:render",
  events: {
    addEventListener(type, cb) {
      window.addEventListener("message", (event) => {
        if (event.data.type === type) {
          event.detail = event.data;
          cb(event);
        }
      });
    }
  }
};
