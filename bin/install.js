#!/usr/bin/env node
/**
 * Install the apple-shortcuts-authoring skill into an agent skills folder.
 *
 *   npx apple-shortcuts-skill                 # -> ~/.claude/skills/apple-shortcuts-authoring
 *   npx apple-shortcuts-skill <target-dir>    # -> <target-dir>
 *
 * Copies SKILL.md, tools/ and examples/ from this package. No dependencies.
 */
const fs = require("fs");
const os = require("os");
const path = require("path");

const target = process.argv[2]
  ? path.resolve(process.argv[2])
  : path.join(os.homedir(), ".claude", "skills", "apple-shortcuts-authoring");

const pkgRoot = path.join(__dirname, "..");
const items = ["SKILL.md", "tools", "examples"];

fs.mkdirSync(target, { recursive: true });
for (const item of items) {
  fs.cpSync(path.join(pkgRoot, item), path.join(target, item), {
    recursive: true,
    force: true,
  });
}
console.log(`apple-shortcuts-authoring skill installed to: ${target}`);
