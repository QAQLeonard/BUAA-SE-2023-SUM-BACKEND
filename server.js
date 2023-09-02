import axios from 'axios';  // 确保已经安装了Axios
import { Server } from "@hocuspocus/server";
import { Database } from "@hocuspocus/extension-database"

function arrayBufferToBase64(buffer) {
  let binary = '';
  let bytes = new Uint8Array(buffer);
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}



const server = Server.configure({
  port: 8002,

  async onConnect() {
    console.log('🔮')
  },

  extensions: [
    new Database({
      fetch: ({ documentName }) => {
        return new Promise((resolve, reject) => {
          axios.get(`http://23.94.102.135:8000/api/v1/pe/docs/${documentName}/data/`, { responseType: 'blob' })
            .then(response => {
              const base64Data = response.data.yjs_data;
              const binaryData = Uint8Array.from(atob(base64Data), c => c.charCodeAt(0));
              resolve(binaryData);
            })
            .catch(error => {
              console.error(error);
              reject(null);

            });
        });
      },
      store: ({ documentName, state }) => {
        return new Promise((resolve, reject) => {
          const base64State = arrayBufferToBase64(state);
          axios.post(`http://23.94.102.135:8000/api/v1/pe/docs/${documentName}/data/`, { yjs_data: base64State })
            .then(() => {
              resolve();
            })
            .catch(error => {
              console.error(error);
              reject();
            });
        });
      },
    }),
  ],
});

server.listen();
