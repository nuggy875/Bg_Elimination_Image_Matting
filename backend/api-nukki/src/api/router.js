/**
 * root api router
 */

const express = require("express");
const nukki = require("./nukki/router");

const router = express.Router();

router.use("/nukki", nukki);

module.exports = router;
