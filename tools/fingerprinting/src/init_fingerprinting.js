/*
 * In this script we use @mdn/browser-compat-data to retrieve a list of browsers with their list of compatible features.
 */

const fs = require('fs');
const path = require("path");
const bcd = require('@mdn/browser-compat-data');

const configPath = path.join(__dirname, "..", "config");
const outputPath = path.join(__dirname, "..", "output");

const browsersFile = path.join(configPath, "browsers.json");
const featuresFile = path.join(configPath, "features-in-scope.txt");
const outFile = path.join(outputPath, "feature_map.json");

const BROWSER_VERSIONS = require(browsersFile);
const FEATURES_IN_SCOPE = fs.readFileSync(featuresFile).toString().split("\n").slice(0, -1);

// toggle whether to check scope
let scopeCheck = true;

let data = new Map();

function init() {
	for (let browserIndex in BROWSER_VERSIONS) {
		let entry = BROWSER_VERSIONS[browserIndex];
		for (let i = entry.min; i <= entry.max; i++) {
			data.set(browserIndex + i, new Set());
		}
	}

	processObjects(bcd.api);
	processObjects(bcd.javascript["builtins"]);

	// postprocess
	for (let key of data.keys()) {
		data.set(key, Array.from(data.get(key)));
	}

	// store to file
	fs.writeFile(outFile, JSON.stringify([...data]), err => {
		if (err) {
			throw err;
		}
	});
}

function processObjects(obj) {
	Object.entries(obj).map(([name, value]) => processCompatObject(name, value))
}

function processCompatObject(name, value) {
	if (scopeCheck && !FEATURES_IN_SCOPE.includes(name)) {
		return;
	}
	if (!value.__compat) {
		return;
	}

	let support = value.__compat.support;
	for (let browserName in BROWSER_VERSIONS) {
		let entry = support[browserName];
		if (Array.isArray(entry)) {
			entry = support[browserName][0];
		}
		let version = Math.floor(entry.version_added); //Not exact, but Opera numbering sucks
		if (!version) {
			continue;
		}

		version = Math.max(version, BROWSER_VERSIONS[browserName].min); //Skip super old versions
		for (let i = version; i <= BROWSER_VERSIONS[browserName].max; i++) {
			data.get(browserName + i).add(name);
		}
	}
}

function update() {
	scopeCheck = false;
	init();

	let str = "var txt = ''; var js = 'var feature_fp_globals = ['; var test = [";
	for (let entry of data.get("chrome" + BROWSER_VERSIONS.chrome.max)) {
		str += `"${entry}",`;
	}
	str += `];
        for (let name in test) {
            if (test[name] in window) {
                txt += test[name] + '\\n';
                js += '"' + test[name] + '",'
            }
        };
        console.log(txt);
        console.log(js + ']');`
	console.log(str);
}

init();
//update();
