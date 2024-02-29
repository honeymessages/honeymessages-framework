import {Connector} from "./connector.js";
import {CREDENTIALS} from "./config.js";

console.log("Testing the credentials in config.js.\nIf everything works, the users list can be fetched.")

let connector = new Connector();
await connector.init(CREDENTIALS);
let users = await connector.getUsers()

console.log("Usernames:", users.map(user => user.username));

if (users.length > 0) {
	console.log("Successfully fetched", users.length, "users.")
}
