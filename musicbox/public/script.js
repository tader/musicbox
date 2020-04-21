document.addEventListener("DOMContentLoaded", () => {
	const app = new Vue({
		el: '#app',
		data: {
			socket: false,
			card: {},
			favorites: [],
			playlists: [],
		},
		methods: {
			assign: assign,
		},
	});

	function webSocketUri(path) {
		const loc = window.location;
		const protocol = (loc.protocol === "https:") ? "wss" : "ws";

		return `${protocol}://${loc.host}${loc.pathname}${path}`;
	}

	function openWebSocket() {
		let socket = new WebSocket(webSocketUri("events"));

		socket.onmessage = (event) => { app.card = JSON.parse(event.data); };
		socket.onopen    = (event) => { connected();                       };
		socket.onerror   = (event) => { console.error(event);              };
		socket.onclose   = (event) => { disconnected();                    };
	}

	function connected() {
		app.socket = true;
	}

	function disconnected() {
		app.socket = false;

		setTimeout(openWebSocket, 1000);
	}

	function loadFavorites() {
		axios.get('/favorites')
			.then((res) => { app.favorites = res.data; })
			;
	}

	function loadPlaylists() {
		axios.get('/playlists')
			.then((res) => { app.playlists = res.data; })
			;
	}

	function assign(fav, content_type) {
		if (fav && fav.id) {
			if (app.card && app.card.card_id) {
				axios.post(`/assign/${app.card.card_id}`, {
					title: fav.name,
					content_type: content_type,
					content_id: fav.id,
					shuffle: false,
				}).then((res) => { app.card = res.data; }).catch((x) => { alert(x); });
			} else {
				// no card
			}
		}
	}

	openWebSocket();
	loadFavorites();
	loadPlaylists();
});
