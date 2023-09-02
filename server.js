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
          axios.get(`http://localhost:8000/api/v1/pe/docs/${documentName}/data/`)
          .then(response => {
            resolve(response.data.yjs_data); // 如果返回的字段是'yjs_data'，请相应地调整这里
          })
          .catch(error => {
            console.error(error);
            reject(null);
          });
        });
      },
      store: ({ documentName, state }) => {
        return new Promise((resolve, reject) => {
          axios.post(`http://localhost:8000/api/v1/pe/docs/${documentName}/data/`, { yjs_data: state }) // 根据后端视图来设置键名
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
