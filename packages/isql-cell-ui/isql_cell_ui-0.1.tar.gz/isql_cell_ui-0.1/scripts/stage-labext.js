// scripts/stage-labext.js
import { mkdirSync, cpSync, writeFileSync } from "fs";
import { resolve } from "path";

const labextDir = resolve('.', 'labextension');
const libDir = resolve('.', 'lib');

mkdirSync(labextDir, { recursive: true });

// Copy compiled output
cpSync(resolve(libDir, 'index.js'), resolve(labextDir, 'index.js'));

// Create minimal runtime package.json
const pkg = {
  name: "sql-python-cell-switch",
  version: "0.1",
  main: "index.js",
  jupyterlab: {
    extension: true
  }
};

writeFileSync(
  resolve(labextDir, 'package.json'),
  JSON.stringify(pkg, null, 2)
);

console.log("labextension/ staged.");
