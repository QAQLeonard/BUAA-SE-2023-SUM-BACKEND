import axios from 'axios';  // 确保已经安装了Axios
import { Server } from "@hocuspocus/server";
import { Database } from "@hocuspocus/extension-database"

const server = Server.configure({
    port: 8002,

  async onConnect() {
    console.log('🔮')
  },

  extensions: [
    new Database({
      fetch: ({ documentName }) => {
        return new Promise((resolve, reject) => {
          axios.get(`http://23.94.102.135:8000/api/v1/pe/docs/${documentName}/data/`,{responseType: 'blob'})
          .then(response => {
            let data = new Uint8Array(response.data);
            resolve(data);
          })
          .catch(error => {
            console.error(error);
            reject(null);
            
          });
        });
      },
      store: ({ documentName, state }) => {
        return new Promise((resolve, reject) => {
          axios.post(`http://23.94.102.135:8000/api/v1/pe/docs/${documentName}/data/`, state, {headers: {
            'Content-Type': 'application/octet-stream'
          }})
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
