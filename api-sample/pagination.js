import axios from "axios";

export function get_all_pages_factory(url) {
	/**
	 * Factory that fetches all pages of the paginated viewset.
	 * Use like this `fetch = paginated_factory('url'); fetch().then(...)`
	 */
	return function paginatedFetcher(next = null, obj_list = []) {
		return axios.get(next ? next : url)
			.then(({data}) => {
				console.log(data);
				obj_list.push(...data["results"])
				if (!data.next) return obj_list
				return paginatedFetcher(data.next, obj_list)
			}).catch(err => console.log(err));
	}
}
