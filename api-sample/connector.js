import axios from "axios";
import {BASE_URL} from "./config.js";
import {get_all_pages_factory} from "./pagination.js";

/**
 * Helper function
 * Uses the URLSearchParams API to convert a JavaScript dictionary to url-encoded data.
 * Use this for content type "application/x-www-form-urlencoded".
 *
 * e.g. {name: "anon", password: "mine"} -> "name=anon&password=mine"
 * @param data
 * @returns {string}
 */
function dictToForm(data) {
	return new URLSearchParams(data).toString();
}

export class Connector {

	/**
	 * To use Connector, create an instance of it and then call init with credentials.
	 * After init is called, an authentication token is fetched and automatically stored for axios.
	 * Afterward, all requests to the HoneyMessages API will be authenticated with this token, and you don't have
	 * to authenticate again.
	 */
	constructor() {
		this.initialized = false;
	}

	async init(credentials) {
		/* Send username and password to the frameworks token-auth endpoint to receive an authentication token. */
		console.log(dictToForm(credentials));
		return axios.post(
			`${BASE_URL}/api/token-auth/`,
			dictToForm(credentials), {headers: {"Content-Type": "application/x-www-form-urlencoded"}}
		).then(response => {
			// Intercept requests and attach Authorization headers to each following request
			axios.interceptors.request.use(function (config) {
				config.headers["Authorization"] = `Token ${response.data["token"]}`;
				return config;
			});
			this.initialized = true;
		}).catch(
			// login failed
			err => {
				console.error("Login failed.", err.message);
			}
		);
	}

	/**
	 * Wrapper for all operations where simply all elements of an API endpoint are fetched.
	 * @param endpoint
	 * @returns {Promise<*[]|AxiosResponse<any>|void>}
	 * @private
	 */
	async _getAll(endpoint) {
		if (!this.initialized) {
			throw new Error("Connector is uninitialized. Call init first.")
		}

		/*
		Usually, you could just do axios.get("url"), but some API endpoints will use pagination to resolve faster
		when there are many results in the database table.
		-> https://www.seobility.net/de/wiki/Pagination
		In detail, only the first 100 entries are returned per page.
		The paginated_factory takes care of this. It fetches the first page
		 */
		const fetch = get_all_pages_factory(`${BASE_URL}${endpoint}`);

		/* Now let's test, if the request is authenticated. */
		return await fetch().then(response => {
			/* It worked. */
			return response;
		}).catch(err => {
			console.error("Something went wrong...", err.message);
			return null;
		})
	}

	/**
	 * Example: Only for reference. You usually want all pages.
	 * Fetches only the first page of the User endpoint.
	 * @returns {Promise<AxiosResponse<any>>}
	 */
	async _getFirstPage(endpoint) {
		if (!this.initialized) {
			throw new Error("Connector is uninitialized. Call init first.")
		}

		/* Now let's test, if the request is authenticated. */
		return await axios.get(`${BASE_URL}${endpoint}`).then(response => {
			/* It worked. */
			return response.data["results"];
		}).catch(err => {
			console.error("Something went wrong...", err.message);
			return null;
		});
	}

	async _post(endpoint, data) {
		if (!this.initialized) {
			throw new Error("Connector is uninitialized. Call init first.")
		}

		/* Now let's test, if the request is authenticated. */
		return await axios.post(
			`${BASE_URL}${endpoint}`,
			data
		).then(response => {
			/* It worked. */
			return response["data"]
		}).catch(err => {
			console.log(err);
			return null;
		});
	}

	/**
	 * Example usage:
	 * Fetches all pages of the User endpoint.
	 * @returns {Promise<*[]|AxiosResponse<any>|void>}
	 */
	async getUsers() {
		return await this._getAll("/api/users/")
	}

	/**
	 * Example usage:
	 * @returns {Promise<*[]|AxiosResponse<any>|void>}
	 */
	async getMessengers() {
		return await this._getAll("/api/messengers/")
	}

	async postMessenger(name) {
		return await this._post("/api/messengers/", {name: name, manual_only: true})
	}

	async postExperiment(name, messengerId) {
		let data = {
			name: "",
			messenger_id: messengerId,
			with_honeypage: true,
			manual: 1 // we only support manual experiments
		}
		if (name && name.length > 0) {
			data["name"] = name;
		}
		return await this._post("/api/experiments/", data)
	}
}
