function JumpTo(t) {
  Status("jumpto?t=" + t);
}

function Search() {
  var url = "ajax/search?q=" + escape(document.form.query.value);
  SendRPC(url, function(response) {
    var results = JSON.parse(response);
    var box = document.getElementById("suggestions");
    var txt = "";
    box.innerHTML = "";
    for (var i = 0; i < results.length; ++i) {
      var r = results[i];
      if (i != 0) {
        txt = " &mdash; ";
      } else {
        txt = "";
      }
      txt += "<a href='javascript:JumpTo(" + r.id + ")'>" + r.name + "</a>";
      box.innerHTML += txt;
    }
  });
}

function Status(command) {
  SendRPC("ajax/" + command, function(response) {
    var r = JSON.parse(response);
    document.getElementById("title").innerHTML = r.track.title;
    document.getElementById("album").innerHTML = r.track.album;
    document.getElementById("artist").innerHTML = r.track.artist;
    document.getElementById("volume").innerHTML = r.volume;
    if (r.volume == 0) {
      document.getElementById("voldown").style.display = "none";
    } else {
      document.getElementById("voldown").style.display = "inline";
    }
    if (r.volume == 100) {
      document.getElementById("volup").style.display = "none";
    } else {
      document.getElementById("volup").style.display = "inline";
    }
    var playbutton = document.getElementById("playbutton");
    if (r.playing) {
      playbutton.src = "static/pause.png";
    } else {
      playbutton.src = "static/play.png";
    }
    if (refresh_timeout != null) {
      clearTimeout(refresh_timeout);
    }
    if (r.time_left > 0 && r.playing) {
      refresh_timeout = setTimeout("Status('status')", r.time_left * 1000);
    }
  });
}

function ChangeVolume(ticks) {
  var command = "changevolume?v=" + ticks;
  Status(command);
}

