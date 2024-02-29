# Init Browser Fingerprinting

## Reference

If you use this fingerprinting approach, please cite the work "Server-Side Browsers: Exploring the Web's Hidden Attack Surface" (Marius Musch, Robin Kirchner, Max Boll, Martin Johns) (AsiaCCS 2022) using the [SSB.bib](./ssb.bib) and this work [honeymessages.bib](../../honeymessages.bib).

## Introduction

Browser fingerprinting relies on browser-feature-compatibility lists from MDN.
We parse those lists to create a map between browser versions and a list of compatible features.
This map is stored as a json file that can be used by the Python code of the honeypot.

The updating process of our fingerprinting process is semi-automated.
Complete the manual steps first: collect the features of the newest Chrome Canary, update the list of browser versions

Only files in the `config` folder need adjustment.

## Update procedure

- Run `npm install`

### Update the latest browser versions

- Manually update the latest browser versions in [config/browser.json](config/browsers.json) with the table from [https://caniuse.com/ciu/comparison](https://caniuse.com/ciu/comparison.

### Collect the features of Chrome Canary

In this step you collect the features of the latest Chrome Canary and insert them in a txt file and the fingerprinting script.

- Make sure the last line in `init_fingerprinting.js` is `update();` otherwise temporarily add that line
- Copy the code via `node init_fingerprinting.js | pbcopy`
- Download and install [Chrome Canary](https://www.google.com/intl/en-gb/chrome/canary/)
- Visit <http://example.com> in Chrome Canary
  - https://example.com allows more features, but is problematic if someone visits the monitor via http
- Paste the copied code into the DevTools console and run it
- Copy the first output and overwrite `config/features-in-scope.txt` with that content (it should be a list of names separated by newlines)
- Copy the second output and replace `feature_fp_globals` in `config/scripts/feature_fp.js`.
- Increment the `VERSION` in `config/scripts/feature_fp.js` (at the top).
- Make sure `update();` in the last line of `init_fingerprinting.js` os commented out again

### Run init fingerprinting to create the feature map

Always do the previous steps first.
Make sure that `npm install` was executed.

    node init_fingerprinting.js

This created `output/feature_map.json`.

### Update FingerprintJS2

- Fetch the latest minified js version of [FingerprintJS](https://github.com/fingerprintjs/fingerprintjs), e.g. from here [fp.min.js](https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js). 
- Place the file in [config/scripts/fp.min](config/scripts/fp.min).
- Update the FingerprintJS version in [config/scripts/fingerprintjs.js](config/scripts/fingerprintjs.js) under `fingerprint2_version`.

### Create the combines fingerprinting script

Run the Python script that combines the fingerprinting scripts.

    cd src/
    python3 combine_scripts.js

This creates [output/fingerprinting.js](output/fingerprinting.js).

### Copy the files into the project folder

A final script copies the generated files to their respective place in the project.

    ./copy_output.sh

Don't forget to run `python3 manage.py collectstatic` so that Django updates the static files.
