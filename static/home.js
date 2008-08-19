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
  var url = "/ajax/search?";
  url = url + "q=" + escape(document.search.query.value);
  // Add a random number to prevent the server from using a cached file??
  // TODO: Is this really necessary, especially given our webserver?
  url = url + "&sid=" + Math.random();
  xmlhttp.open("GET", url, true);
  xmlhttp.send(null);
}
