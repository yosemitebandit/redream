(function () {

var RedreamVideo = window.RedreamVideo = function (selector, url) {
  var $dom = $(selector);
  var popcorn = Popcorn.smart(selector, url);
  var video = popcorn.video;

  popcorn.on(
    'canplay', 
    function () {
      console.log('canplay!');
      var ww = $dom.width();
      var wh = $dom.height();
      var w_ratio = ww / wh;
      var vw = video.videoWidth;
      var vh = video.videoHeight;
      var v_ratio = vw / vh;
      if (w_ratio === 1) {
        // square
        console.log('implement me!');
      }
      else if (w_ratio > 1) {
        // landscape
        if (v_ratio === 1) {
          console.log( 'a0' );
          // video is square
          // video width align to wrap width
          // video marginTop is always negative
          video.style.width = ww + 'px';
          video.style.marginTop = ((ww - (vw * wh / ww)) / 2) + 'px';
        }
        else if (v_ratio > 1) {
          // video is landscape too
          if (v_ratio === w_ratio) {
            console.log( 'a1' );
            // same aspect ratio
            video.style.width = ww + 'px';
          }
          else if (v_ratio > w_ratio) {
            console.log( 'a2' );
            // video is wider than wrap
            // video height is align to wrap height
            // video marginLeft is always negative
            video.style.height = wh + 'px';
            video.style.marginLeft = ((ww - (vh * ww / wh)) / 2) + 'px';
          }
          else {
            console.log( 'a3' );
            // video is shorter than wrap
            // video width align to wrap width
            // video marginTop is always negative
            video.style.height = wh + 'px';
            video.style.marginLeft = ((ww - (vh * ww / wh)) / 2) + 'px';
          }
        }
        else {
          console.log( 'a4' );
          // video is portrait
          // video is shorter than wrap
          // video width align to wrap width
          // video marginTop is always negative
          video.style.height = wh + 'px';
          video.style.marginLeft = ((ww - (vh * ww / wh)) / 2) + 'px';
        }
      }
      else {
        // portrait
        console.log('implement me!');
      }
    }
  );

  console.log( 'hey!!', $dom );
  this.dom = $dom[0];

  console.log( this.dom );

  $dom.addClass( 'popcorn-wrap' );
  video.removeAttribute('controls');
  video.muted = true;
  popcorn.loop(true);
  
  RedreamVideo._global.push(this);
  this.popcorn = popcorn;
};

RedreamVideo._global = [];

// static
// ===============================================

RedreamVideo.globalHalt = function () {
  $.each(
    RedreamVideo._global, 
    function (i, rv) {
      if (!rv.popcorn.isDestroyed) {
        rv.popcorn.pause();
      }
    }
  );
};

RedreamVideo.globalPlay = function () {
  $.each(
    RedreamVideo._global, 
    function (i, rv) {
      if (!rv.popcorn.isDestroyed) {
        rv.popcorn.play();
      }
    }
  );
};

RedreamVideo.globalMute = function () {
  $.each(
    RedreamVideo._global, 
    function (i, rv) {
      if (!rv.popcorn.isDestroyed) {
        rv.popcorn.video.muted = true;
      }
    }
  );
};

RedreamVideo.globalUnmute = function () {
  $.each(
    RedreamVideo._global, 
    function (i, rv) {
      if (!rv.popcorn.isDestroyed) {
        rv.popcorn.video.muted = false;
      }
    }
  );
};

// instance
// ===============================================

RedreamVideo.prototype.play = function () {
  if (this.popcorn && !this.popcorn.isDestroyed) {
    this.popcorn.play();
  }
  return this;
};

RedreamVideo.prototype.pause = function () {
  if (this.popcorn && !this.popcorn.isDestroyed) {
    this.popcorn.pause();
  }
  return this;
};

RedreamVideo.prototype.cue = function (time, cb) {
  if (this.popcorn && !this.popcorn.isDestroyed) {
    this.popcorn.cue(time, cb);
  }
  return this;
};

RedreamVideo.prototype.bringFront = function () {
  $.each( 
    RedreamVideo._global,
    function (i, rv) {
      $(rv.dom).removeClass('is-above');
    }
  );
  $(this.dom).addClass('is-above');
  return this;
};

RedreamVideo.prototype.fade = function () {
  $(this.dom).addClass('is-hiding');
  return this;
};

RedreamVideo.prototype.unfade = function () {
  $(this.dom).removeClass('is-hiding');
  return this;
};

})();