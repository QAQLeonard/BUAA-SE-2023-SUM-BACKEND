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
          axios.post(`http://23.94.102.135:8000/api/v1/pe/docs/${documentName}/data/`, { yjs_data: state }) // 根据后端视图来设置键名
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
