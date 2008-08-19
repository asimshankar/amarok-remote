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

