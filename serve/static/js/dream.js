/**
 * dream
 */
(function() {

var $wrapper;
var tmpl_video_wrap;
var prefix_id = 'video_';
var is_inited = false;
var buffers = window.buffers = [];
var loaded_video = [];

var init = function () {
  console.log('init');

  $wrapper = $('#wrapper');
  tmpl_video_wrap = $.trim( $('#tmpl-video-wrap').html() );

  startLoading();
  // setTimetout( switching, 10000 );
};

var startLoading = function () {
  if (DREAMCLIPS.length !== loaded_video.length) {
    console.log( 'load another video' );
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
    }

    setTimeout(startLoading, 1000);
  }
};

var switching = function () {  
};

$(init);

})();
