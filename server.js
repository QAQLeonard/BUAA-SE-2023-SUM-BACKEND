import { Server } from "@hocuspocus/server";
import { Database } from "@hocuspocus/extension-database"
import mysql from "mysql2/promise";

const pool = mysql.createPool({
  host: "localhost",
  user: "root",
  database: "se_sum",
  password: "ef515b982e119ceb",
});


const server = Server.configure({
  port: 8002,

  async onConnect() {
    console.log('🔮')
  },

  extensions: [
    new Database({
      fetch: async ({ documentName }) => {
        const connection = await pool.getConnection();
        try {
          const [rows] = await connection.query(
            'SELECT yjs_data FROM docs WHERE doc_id = ? ORDER BY id DESC LIMIT 1',
            [documentName]
          );
          connection.release();
          return rows.length ? rows[0].data : null;
        } catch (error) {
          connection.release();
          throw error;
        }
      },
      store: async ({ documentName, state }) => {
        const connection = await pool.getConnection();
        try {
          await connection.query(
            `INSERT INTO docs (doc_id, yjs_data) VALUES (?, ?)
             ON DUPLICATE KEY UPDATE yjs_data = ?`,
            [documentName, state, state]
          );
          connection.release();
        } catch (error) {
          connection.release();
          throw error;
        }
      },
    }),
  ],
});

server.listen();
