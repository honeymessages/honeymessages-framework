import {Connector} from "./connector.js";
import {CREDENTIALS} from "./config.js";


let connector = new Connector();
await connector.init(CREDENTIALS);

async function postOrGetMessengerByName(name) {
	console.debug(`Checking if the messenger ${name} already exists.`);
	let messengers = await connector.getMessengers();
	console.log(messengers);

	/*
	Super cool shorthand to create a JavaScript dictionary from our list of messengers with Object.fromEntries().
	We map each entry (messenger) of the array (messengers) to a tuple where the first element is the name
	(which will be the key in out dictionary) and the messenger ID (which will be the value in our dictionary).
	Object.fromEntries then creates the dictionary (or Object) from the Array we created inline.
	 */
	let messengerDict = Object.fromEntries(
		messengers.map(messenger => [messenger.name, messenger.id])
	)

	// console.debug(messengerDict)

	// check if the messenger we want to create already exists
	if (Object.keys(messengerDict).includes(name)) {
		console.debug(`${name} already exists. It's ID is ${messengerDict[name]}.`);
		return messengerDict[name];
	} else {
		// the messenger name is not known to the backend, so let's POST it
		let data = await connector.postMessenger(name);
		console.debug(`${name} was created with ID ${data.id}.`)
		return data.id;
	}
}

/**
 * Example function to create an experiment for a messenger and print the created HoneyPage link.
 * @param messengerId
 * @returns {Promise<T>}
 */
async function createExperiment(messengerId) {
	let response = await connector.postExperiment("Test", messengerId);
	if (response) {
		console.log("A new HoneyPage was created: ", response["honeypage_link"])
	}
	return response;
}

// Get ID of messenger "ABC" and create it if it doesn't exist
let messengerId = await postOrGetMessengerByName("Signal")

// Create an experiment for this messenger and get the honeydata
await createExperiment(messengerId);
