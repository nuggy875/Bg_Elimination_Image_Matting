const express = require("express");
const router = express.Router();

const test = require("./test");

router.get("/ping", test.ping);
router.get("/python2", test.python);

module.exports = router;
