var xmlhttp = createXmlHttpRequestObject();
function createXmlHttpRequestObject() {
	var xmlhttp;
	// IE compatibility
	if (window.ActiveXObject) {
		try {
			xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
		} catch (e) {
			xmlhttp = false;
		}
	} else {
		try {
			xmlhttp = new XMLHttpRequest()
		} catch (e) {
			xmlhttp = false;
		}
	}
	if (!xmlhttp) {
		console.log("Cannot create XHR object.")
	} else {
		return xmlhttp;
	}
}

function process() {
	if (xmlhttp.readyState==0 || xmlhttp.readyState==4) { 
		xmlhttp.open('GET', '/cgi-bin/get_connected_users.py', true);
		xmlhttp.onreadystatechange = handleServerResponse;
		xmlhttp.send(null);
	} else {
		console.log('xhr object is not ready.')
	}
}

function handleServerResponse() {
	if (xmlhttp.readyState == 4) {
		if (xmlhttp.status == 200) {
			responseJSON = JSON.parse(xmlhttp.response)

			var keys = []
			for (k in responseJSON) { keys.push(k); }
			if (k.length == 0) {
				var elem = document.getElementById('no-action-response');
				if (elem != null) {
					elem.remove();
				}
				var resp = document.createElement('div')
				resp.setAttribute('class', 'prompt')
				resp.setAttribute('id', 'no-action-response')
				resp.innerHTML = "There are no users connected. You can be the first. :)"
				this.parentElement.appendChild(resp);
				return;
			}

			// else create a display layout for the attained data
			var elems = document.getElementsByClassName('prompt');
			for (elem in elems) { elem.remove(); }
			elems = document.getElementsByClassName('response');
			for (elem in elems) { elem.remove(); }

			// creating a new element to insert data
			var hdr = document.createElement('header')
			hdr.innerHTML = "This is the list of systems that are connected to this exchange."
			hdr.setAttribute('class', 'prompt')

			var tbl = document.createElement('table')
			tbl.innerHTML += "<tr><th>IP address</th><th>Server name</th><th>Available shared size</th></tr>";
			for (sessid in responseJSON) {
				tbl.innerHTML += "<tr><td>"+responseJSON[sessid].IP_ADDRESS+"</td><td>"+responseJSON[sessid].SERVER_NAME+"</td><td>"+responseJSON[sessid].'SHARED_SIZE'+"</td></tr>";
			}
			tbl.innerHTML += "</table>";

			document.getElementById('connected_users').getElementsByTagName('article').appendChild(hdr);
			document.getElementById('connected_users').getElementsByTagName('article').appendChild(tbl);
		}
	}
}
