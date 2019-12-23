require("./config/env");
const server = require("./src/server");
const logger = require("./src/utils/logger");

// port는 직접 넣은 env에서 먼저 찾고, config를 찾은후 default를 세팅한다.
const port = process.env.PORT || 3000;
server.set("port", port);

// 실행된 서버 객체
let serve;

async function start() {
  logger.info(`${process.env.PORT}포트 에 연결을 시작합니다.`);

  // 실행된 서버 객체를 담는다.
  serve = await new Promise((resolve, reject) => {
    const s = server.listen(port, error => {
      if (error) return reject(error);
      resolve(s);
    });
  });
}

// start server
start()
  .then(() => {
    logger.info(`api 서버가 ${port} 포트에서 실행중입니다.`);
  })
  .catch(error => {
    logger.error("서버 실행에 실패하였습니다", error);
    if (serve) server.close();
  });
