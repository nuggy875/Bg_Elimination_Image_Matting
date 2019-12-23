// 간단한 pino logger다.
const pino = require('pino');

module.exports = pino({
  safe: true,
  prettyPrint: true,
  name: 'API_SERVER',
});
