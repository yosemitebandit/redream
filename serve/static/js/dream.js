/**
 * dream
 */
(function() {

window.isPlayingContiously = true;
var $wrapper;
var tmpl_video_wrap;
var prefix_id = 'video_';
var is_inited = false;
var buffers = window.buffers = [];
var loaded_video = [];
var cursor;
var MILSEC_SWITCHING = 5000;
var MILSEC_TRANSITION = 500;

var init = function () {

  $wrapper = $('#wrapper');
  tmpl_video_wrap = $.trim( $('#tmpl-video-wrap').html() );
  twitter_init();

  if (DREAMCLIPS.length) {
    startLoading();
    setTimeout( switching, MILSEC_SWITCHING );
  }
};

var twitter_init = function () {
  var $handle = $('#twitter-handle');
  var $submit = $('#twitter-handle-submit');
  if ($handle.length !== 1 || $submit.length !== 1) {
    return;
  }
  $submit.one(
    'click',
    function (ev) {
      $.post(
        TWITTER,
        {handle: $handle.val()},
        function (data, successText, xhr) {
          var $parent = $submit.parent();
          $submit.fadeOut(
            500,
            function () {
              $parent.append('Thanks!');
            }
          );
        }
      );
    }
  );
};

var startLoading = function () {
  if (DREAMCLIPS.length !== loaded_video.length) {
    var i = loaded_video.length;
    var video_meta = DREAMCLIPS[ i ];
    var id = prefix_id + i;
    $wrapper.append(Mustache.render(tmpl_video_wrap, {ID: id}));
    var rv = new RedreamVideo( '#' + id, video_meta.clip );
    loaded_video.push( video_meta.clip );
    buffers.push( rv );

    if (!is_inited) {
      rv.play().bringFront();
      is_inited = true;
      cursor = i;
    }
    else {
      rv.play().fade();
    }

    setTimeout(startLoading, 1000);
  }
};

var getNextCusor = function () {
  var next = cursor + 1;
  if (next >= buffers.length) {
    next = 0;
  }
  return next;
};

var switching = function () {
  if (DREAMCLIPS.length === 1) {
    return false;
  } 
  var current_video = buffers[cursor].bringFront();
  var next = getNextCusor();
  var next_video = buffers[next];
  next_video.unfade();
  setTimeout(
    function () {
      current_video.fade();
      if (window.isPlayingContiously) {
        cursor = next;        
        setTimeout( switching, MILSEC_SWITCHING );
      }
    },
    MILSEC_TRANSITION);
};

$(init);

})();
