(function tryEmbedImage() {
	/**
	 * Find the element with id "img-placeholder".
	 * Find the page url from the element with id "a_current_page".
	 * Craft an url for an img (one.gif).
	 * Insert that image to the placeholder.
	 */

	let a_current_page = document.getElementById("a_current_page");
	let placeholder_p = document.getElementById("img_text_placeholder");
	let placeholder = document.getElementById("img_placeholder");

	if (a_current_page && placeholder_p && placeholder) {
		let url = new URL(a_current_page.href);
		url.search = "";
		url.hash = "";
		let href = url.href;
		href = href.endsWith("/") ? href : href + "/";

		// insert img
		let img = document.createElement("img");
		img.src = href + "one.gif/";
		placeholder.appendChild(img);
		placeholder_p.innerHTML = "JavaScript injected an invisible image into this page: <pre>" + img.src + "</pre>";
	}
})();
