const { PythonShell } = require("python-shell");

// ping test
async function ping(req, res) {
  console.log(req);
  const test = {
    text: "hi"
  };

  try {
    res.status(200).json(test);
  } catch (err) {
    res.status(500).send("fail");
  }
}

// python test
async function python(req, res) {
  let options = {
    mode: "text",
    pythonPath: "",
    pythonOptions: ["-u"],
    scriptPath: "./python-code/detectron2/demo",
    args: ["value1", "value2"]
  };
  let value1;

  function firstData() {
    return new Promise((resolve, reject) => {
      return PythonShell.run("demo_test.py", options, function(err, results) {
        resolve(results);
      });
    });
  }

  function secondData(data) {
    options = {
      ...options,
      scriptPath: "./python-code"
    };
    return new Promise((resolve, reject) => {
      return PythonShell.run("imageMatting_test.py", options, function(
        err,
        results
      ) {
        resolve(`${results}-${data}`);
      });
    });
  }

  value1 = await firstData();
  value2 = await secondData(value1);
  console.log("mergedResult", value2);
}

module.exports = {
  ping,
  python
};
