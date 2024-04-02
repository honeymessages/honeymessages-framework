# Honeymessages Framework

## Citation

**A Black-Box Privacy Analysis of Messaging Service Providers’ Chat Message Processing**

If you use our code, please cite our paper (to appear at PETS 2024):

```bibtex
@inproceedings{kirchner2024:honeymessages,
  title={A {B}lack-{B}ox {P}rivacy {A}nalysis of {M}essaging {S}ervice {P}roviders' {C}hat {M}essage {P}rocessing},
  author={Kirchner, Robin and Koch, Simon and Kamangar, Noah and Klein, David and Johns, Martin},
  booktitle={Proceedings on {P}rivacy {E}nhancing {T}echnologies ({PoPETs})},
  year={2024}
}
```

## Description

This repository contains the Honeymessages framework in a dockerized setup, setup and usage instructions,
an [evaluation example](#optional-using-the-data) and an [API connector](#optional-api-connector).

The Honeymessages framework is a black-box messenger analysis framework published with our PETS 2024 paper
"A Black-Box Privacy Analysis of Messaging Service Providers' Chat Message Processing" ([kirchner2024:honeymessages](#citation)).
It combines a honeypot and control serve with REST API to create, manage and monitor honeytoken-based experiments.

The framework's API and honeypot share a domain.
Only the /api path is routed to the API.
The remaining arbitrary subdomains are all served and monitored
by the honeypot module.

After a messenger has been registered with the framework, experiments can be created for it using different types of
honeytokens. Most prominently, honeypages can be used. These are monitored web pages with a distinctive URL. They
offer different types of resources to detect what resources a visitor requests. Also, they contain outgoing links to
other honeypages to detect crawling of links. Each honeypage has a random and unique subdomain that is connected to
the experiment and messenger it was created for.

A messenger is tested in an experiment by first creating a new experiment with honey tokens in the framework.
For this example, a honeypage will be used. This honeypage is assigned by a framework and has a unique URL.
This URL is transmitted in a one-to-one chat using the messenger under test. Both chat partners in this conversation
are controlled by the researcher conducting the experiment. Since the URL is randomly generated, they are very unlikely
to be guessed. Instead, the URL is "leaked" in a controlled fashion via the messenger's chat.
If visits to the URL are recorded after the chat, the visits can be attributed to the respective messenger.
Thus, if access to the URL happens from, e.g., a variety of IP addresses, the messaging provider must have used, processed or shared the URL.

Follow this README to set up the framework locally and serve your own honeypage.
You can create your own [messenger](#31-create-a-messenger) and [experiment](#32-create-an-experiment-for-that-messenger) instances and test the logging functionality.
Use the provided [initial database](backend/run/dev.sqlite3) and plot an [evaluation](#optional-using-the-data) right away, or set up your [own DB](#create-a-new-database) and collect data in your own experiments.

## Requirements

_This guide was tested on a MacBook Pro 2019 running macOS Sonoma 14.3.1._

See the [PETS Instructions](#pets-instructions) when using a preinstalled VM with Docker installed that is already reachable via Internet.

- You will need [Docker](https://docs.docker.com/engine/install) and [docker compose](https://docs.docker.com/compose/install/).
- We require GeoIP2's city database. Please download [GeoLite2-City.mmdb](https://git.io/GeoLite2-City.mmdb) from [P3TERX/GeoLite.mmdb](https://github.com/P3TERX/GeoLite.mmdb) and place it in `run/geoip/GeoLite2-City.mmdb` (~50MB) and `GeoLite2-ASN` (~8MB). You can use the script below to fulfill this task.

```bash
# assuming you are in the honeymessages-framework directory
./scripts/download-files.sh
```

The framework can easily be managed using the corresponding browsable API.
For this local setup you will need to update the `/etc/hosts` file on your host machine, since the framework requires a domain with TLD and arbitrary subdomains.

```bash
# add these lines somewhere in /etc/hosts
127.0.0.1       localtest.me
127.0.0.1       api.localtest.me
```

## Framework Setup Demo

![](backend/static/honey-docker_150px.png)

This is the proof-of-concept demo to run the _honey messages_ framework via Docker.

### 1. Run the framework

Use the script to start or fully restart the framework.

```sh
# Start or restart the framework via Docker
./scripts/full-restart.sh
```

### 2. Visit the framework via browser

The default domain of this setup is [http://api.localtest.me/api/](http://http://api.localtest.me/api/).
After visiting the URL, the first thing you want to do is to log in with the default user:

**Username**: honey
**Password**: messages

**Important** The framework doubles as a control server and a honeypot. You will only reach the browsable API if you
use the correct URL for it. All other subdomains and paths will lead to a honeypage. The framework serves all paths and
subdomains and logs access to it.
Use the `api.` subdomain and `/api/` path (with the slash) to reach the API.
You can still visit URLs outside the API to test the honeypages, e.g., [test.localtest.me/](http://test.localtest.me).
Keep in mind that once you are logged in, the honeypages will recognize your session cookies and create less logs for
your visits. If you don't want that, try using an incognito tab.

Hint: _Remember to use a secure password in production._
Caveat: _Please pay attention to the URL. Firefox, for example, likes to redirect to https. This setup uses http locally, so keep
that in mind._
Caveat: _Please make sure you updated your hosts file as described in the [Requirements](#requirements)._

### 3. Use the framework

Now, it is time to utilize the framework.

#### 3.1. Create a messenger

Hint: _Skip this step if the messenger to test already exists._

Use the browsable API to create a new messenger. On the start page, either click on the link next to
[messengers](http://api.localtest.me/api/messengers/), or visit the corresponding URL.

Fill out the form and enter a name for the messenger, e.g., "Signal". Visit the messenger API endpoint in the
browsable API again, and you should see a new entry for your messenger.
_The messenger was automatically given an ID and a code name._

#### 3.2 Create an experiment for that messenger

Now that you know how to create messengers, you can follow similar steps to create experiments for that messenger.
Visit the [experiments](http://api.localtest.me/api/experiments/) API endpoint and fill out the form at the bottom.
Give the experiment a name, e.g., "Signal Honeypage", choose the messenger in the drop-down field and select which
honeydata types the experiment shall receive. You can choose between **one of the following**. Refer to the
paper to learn more about each experiment type.

- honeypage: a regular experiment with a honeypage that has links to other honeypages
- meta honeypage: a honeypage but additionally with meta HTML tags
- suspicious honeypage: a honeypage with harmless, but suspicious files
- honeymail: a Gmail address "+" unique tokens

Hint: _Add your own base Gmail address in BASE_HONEY_EMAIL_ADDRESS in [.env/.env.dev](.env/.env.dev) for a functioning
honeymail._

#### 3.3 Use the honey data

Inspect your newly created experiment in the list of experiments, i.e., the [experiments](http://api.localtest.me/api/experiments/) API endpoint.
Click on it's "url". Inspect the experiment in JSON format. Apart from ID, url and name of the messenger and experiment,
the data will include the honeytokens. If you used any form of honeypage, a "honeypage_link" entry will exist.
You can copy the link and use it.

Since the framework is only hosted locally right now, you will not be able to reach the URL from another machine.
Just try visiting the link in an incognito tab. You will see a honeypage which you can read. You can also visit
outgoing links to other honeypages.

Come back the API and look at the experiment data again. You should see entries in the "access_logs" list.
If you executed JavaScript with your browser, there will also be logs for browser fingerprints.

Exemplary data is shown here:

```json
{
  "url": "http://api.localtest.me/api/experiments/1/",
  "id": 1,
  "name": "Test Experiment",
  "messenger_id": 1,
  "messenger": "http://api.localtest.me/api/messengers/1/",
  "messenger_name": "Signal",
  "messenger_str": "Signal",
  "honeymail": null,
  "honeymail_address": "",
  "honeypage": "http://api.localtest.me/api/honeypages/1/",
  "honeypage_link": "http://scheming-organ-revealing.localtest.me",
  "with_honeypage": false,
  "with_suspicious_honeypage": false,
  "with_meta_tags_honeypage": false,
  "with_honeymail": true,
  "creator": "root",
  "created_at": "2024-02-23T18:22:40.881139+01:00",
  "start_at": null,
  "finished_at": null,
  "access_logs": [
    "http://api.localtest.me/api/access_logs/61/",
    "http://api.localtest.me/api/access_logs/60/",
    "http://api.localtest.me/api/access_logs/59/",
    "http://api.localtest.me/api/access_logs/58/"
  ],
  "fingerprint_logs": [],
  "browser_fingerprint_logs": []
}
```

### 4. Acquire an Authentication Token

If you want to interact with the honeymessages framework's REST API, first create the user account you want to use, using `./scripts/create-admin.sh`.
Then visit the frameworks [admin page](https://api.honey.ias-lab.de/admin) and specifically go to [admin/authtoken/tokenproxy](https://api.honey.ias-lab.de/admin/authtoken/tokenproxy/).
Select your user account in the list and copy the corresponding key.

### Stop the Framework

Simply stop the docker containers using the stop script.

```bash
./scripts/stop.sh
```

##### Conclusion

This concludes the tutorial on how to setup the honey messages framework. For real-world tests, you will need a public
domain with wildcard subdomains to run tests on messengers. Django and docker compose make it really easy to add a
web server into the setup that serves the static files. Also, you may want to use a faster database in production, e.g.,
[PostgreSQL with Django](https://docs.djangoproject.com/en/5.0/ref/databases/).

## Useful commands

| Script             | Purpose                                      |
| ------------------ | -------------------------------------------- |
| `full-restart.sh`  | Brings everything down, rebuilds, and starts |
| `create-admin.sh`  | Helps to create a new admin user             |
| `collectstatic.sh` | Updates the static files                     |

### Create a new database

This repository comes with an initialized database include a default user for the framework. You can delete the SQLite
database. When starting the framework the next time, a fresh SQLite database is created. You then need to let Django
create the tables and then create a new user account for the framework.

```shell
# Rename the current database as backup
mv backend/run/dev.sqlite3 backend/run/dev.sqlite3_bak

# Restart the framework
./scripts/full-restart.sh

# initialize DB tables
python3 backend/manage.py migrate

# create new superuser
./scripts/create-admin.sh
```

## (Optional) Update browser fingerprinting

This repository includes the required files for browser fingerprinting, but they have to be updated in a semi-automated way.
A detailed step-by-step description is given in `tools/fingerprinting/README.md`.

---

## (Optional) Using the data

Evaluation and analysis works best using iPython/Jupyter notebooks to be able to directly use the Django models.
To demonstrate the approach, the [backend/analysis/artifacts.ipynb](backend/analysis/artifacts.ipynb) notebook
aggregates data from the framework, stores it in JSON format (analysis/out/timings) and plots a scatterplot showing
when a messenger's honeypage was accessed.

### Requirements

For this notebook, you will need Jupyter on your machine.

### Instructions

Go to the `backend/analysis` directory and inspect the corresponding [README](backend/analysis/README.md).
Follow the instructions and use the provided start and stop scripts to open or close the notebook.

---

## (Optional) API Connector

Interacting with the framework using Python is very straight forward, as the framework itself is written in Python,
and the analysis routine demonstrates the approach.
This repository also includes a simple API connector written in Node.Js to demonstrate how the REST API can be used with
different programming languages.

See [api-sample/README.md](api-sample/README.md) for further information.

---

## PETS Instructions

These are instructions, specifically for the Ubuntu Server VMs offered by the PETS conference.

1. clone the repository: `git clone https://github.com/honeymessages/honeymessages-framework`
2. move into the directory: `cd honeymessages-framework`
3. run `./scripts/download-files.sh`
4. Configure your PETS VM hostname in `.env/.env.dev`. Enter the PETS VM hostname without protocol into `DOMAIN_NAME`. Enter the same domain but with a dot before it into SESSION_COOKIE_DOMAIN and CSRF_COOKIE_DOMAIN. See this example for reference.

```
DOMAIN_NAME=<DOMAIN>-docker.artifacts.measurement.network
SESSION_COOKIE_DOMAIN=.<DOMAIN>-docker.artifacts.measurement.network
CSRF_COOKIE_DOMAIN=.<DOMAIN>-docker.artifacts.measurement.network
```

5. Run the startup script `./scripts/full-restart.sh`. 

Please note that step 2 includes a 58 MB download, which may take a few minutes on the VM. Afterwards, the containers should appear in `docker ps`. 

The running framework should now be reachable via browser by using the PETS VM’s hostname.
Visit `http://<DOMAIN>-docker.artifacts.measurement.network/` like this or with arbitrary path to reach a honey page. Visit `http://<DOMAIN>-docker.artifacts.measurement.network/api/` to see the API starting page. Remember that default login is set to username “honey” and password “messages” and that you can find the login button on the top right.

It is important to note that the framework requires arbitrary subdomains to function completely. This is not available by the PETS network. However, running the framework like this and visiting the API page shows that the setup functions.
