const express = require("express");
const router = express.Router();

const test = require("./test");

router.get("/ping", test.ping);
router.get("/python-test", test.python);

module.exports = router;
