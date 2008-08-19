function Search() {
  var xmlhttp = CreateXMLHttpRequest();
  if (xmlhttp == null) {
    alert("AJAX doesn't seem to be supported by your browser. Can't search");
    return;
  }
  xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState == 4) {  // 4 = COMPLETED
      document.getElementById("suggestions").innerHTML = xmlhttp.responseText;
    }
  };
  var url = "ajax/search?";
  url = url + "q=" + escape(document.search.query.value);
  // Add a random number to prevent the server from using a cached file??
  // TODO: Is this really necessary, especially given our webserver?
  url = url + "&sid=" + Math.random();
  xmlhttp.open("GET", url, true);
  xmlhttp.send(null);
}

function SetTrackInfo(track) {
  document.getElementById("title").innerHTML = track.title;
  document.getElementById("album").innerHTML = track.album;
  document.getElementById("artist").innerHTML = track.artist;
}

function Status(command) {
  var xmlhttp = CreateXMLHttpRequest();
  if (xmlhttp == null) {
    alert("AJAX doesn't seem to be supported by your browser. Can't search");
    return;
  }
  xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState == 4) {  // 4 = COMPLETED
      track = JSON.parse(xmlhttp.responseText)
      SetTrackInfo(track);
    }
  };
  xmlhttp.open("GET", "ajax/" + command, true);
  xmlhttp.send(null);
}

