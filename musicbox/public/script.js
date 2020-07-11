document.addEventListener("DOMContentLoaded", () => {
	const app = new Vue({
		el: '#app',
		data: {
			socket: false,
			card: {},
			favorites: [],
			playlists: [],
			zones: [],
		},
		methods: {
			assign: assign,
			setShuffle: setShuffle,
			zonesChanged: zonesChanged,
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

	function loadZones() {
		axios.get('/discover')
			.then((res) => { app.zones = res.data; })
			;
	}

	function setShuffle(shuffle) {
		const card = app.card;

		if (card && card.card_id) {
			axios.post(`/assign/${card.card_id}`, {
				title: card.title,
				content_type: card.content_type,
				content_id: card.content_id,
				shuffle: shuffle,
			}).then((res) => { app.card = res.data; }).catch((x) => { alert(x); });
		} else {
			// no card
		}
	}

	function assign(fav, content_type, shuffle) {
		if (fav && fav.id) {
			if (app.card && app.card.card_id) {
				axios.post(`/assign/${app.card.card_id}`, {
					title: fav.name,
					content_type: content_type,
					content_id: fav.id,
					shuffle: shuffle,
				}).then((res) => { app.card = res.data; }).catch((x) => { alert(x); });
			} else {
				// no card
			}
		}
	}

	function zonesChanged(event) {
		const selected = [...event.target.options]
		                     .filter((x) => x.selected)
		                     .map((x)=>x.value);
		
		axios.put("/zones", selected)
			.then((res) => { }).catch((x) => { alert(x); });
	}

	openWebSocket();
	loadFavorites();
	loadPlaylists();
	loadZones();
});
