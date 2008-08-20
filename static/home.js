function Search() {
  var url = "ajax/search?";
  url = url + "q=" + escape(document.search.query.value);
  SendRPC(url, function(response) {
    document.getElementById("suggestions").innerHTML = response;
  });
}

function Status(command) {
  SendRPC("ajax/" + command, function(response) {
    var r = JSON.parse(response);
    document.getElementById("title").innerHTML = r.track.title;
    document.getElementById("album").innerHTML = r.track.album;
    document.getElementById("artist").innerHTML = r.track.artist;
    var playbutton = document.getElementById("playbutton");
    if (r.playing) {
      playbutton.src = "static/pause.png";
    } else {
      playbutton.src = "static/play.png";
    }
  });
}

