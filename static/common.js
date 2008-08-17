// Browser specific XMLHttpRequest creation
// From: http://www.w3schools.com/Ajax/ajax_browsers.asp
function CreateXMLHttpRequest() {
  var ret = null;
  try { // Firefox, Opera 8.0+, Safari
    ret = new XMLHttpRequest();
  } catch (e) { // Internet Explorer
    try {
      ret = new ActiveXObject("Msxml2.XMLHTTP");
    } catch (e) {
      try {
        ret = new ActiveXObject("Microsoft.XMLHTTP");
      } catch (e) {
        ret = null;
      }
   }
 }
 return ret
}

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
