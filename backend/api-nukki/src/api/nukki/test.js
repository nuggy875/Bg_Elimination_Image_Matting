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
  res.send("Hi! This is Nukki:)");
  console.log('Segmentation Proceeding...')
  let options = {
    mode: "text",
    pythonPath: "",
    pythonOptions: ["-u"],
    // args: ["value1", "value2"],
    scriptPath: "./python-code/detectron2/demo",
  };
  let value1;

  function firstData() {
    return new Promise((resolve, reject) => {
      return PythonShell.run("demo.py", options, function(err, results) {
        resolve(results); 
      });
    });
  }

  function secondData() {
    options = {
      ...options,
      scriptPath: "./python-code"
    };
    return new Promise((resolve, reject) => {
      return PythonShell.run("imageMatting.py", options, function(err, results) {
        resolve(results);
      });
    });
  }
  value1 = await firstData();
  console.log(value1+'\n\n')
  console.log('Matting Proceeding...')
  value2 = await secondData();
  console.log(value2);

}

module.exports = {
  ping,
  python
};


/*
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
        //resolve(`${results}-${data}`);
        resolve(`${results}`)
      });
    });
  }
*/