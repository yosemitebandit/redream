/**
 * dream
 */
(function() {

var video_hash = {
  '20526565': 'http://av.vimeo.com/71427/795/41518371.mp4?aksessionid=25a238d012dcb3822562ee3a4151e6b4&token=1363996617_22f9ff633c526e9c3dee3c938739c338'
  , '32958521': 'http://av.vimeo.com/46287/006/74867996.mp4?aksessionid=312d134c2a88d2cb01e030588cd0e245&token=1363997165_4423d8225f80cbbba621a016c8629cc2'
  , '18280328' : 'http://av.vimeo.com/43382/164/36199250.mp4?aksessionid=1ddc1b47e04db75cd42d21aef00fede6&token=1363997231_b7575d9b4b377e2b33e14645cd277610'
};

var video_list = [];
var loaded_video = [];
for (var _key in video_hash) {
  video_list.push( video_hash[ _key ] );
}

var $wrapper;
var tmpl_video_wrap;
var prefix_id = 'video_';
var is_inited = false;
var buffers = window.buffers = [];

var init = function () {
  console.log('init');

  $wrapper = $('#wrapper');
  tmpl_video_wrap = $.trim( $('#tmpl-video-wrap').html() );

  // startLoading();
  // setTimetout( switching, 10000 );
};

var startLoading = function () {
  if (video_list.length !== loaded_video.length) {
    console.log( 'load another video' );
    var i = loaded_video.length;
    var url = video_list[ i ];
    var id = prefix_id + i;
    $wrapper.append(Mustache.render(tmpl_video_wrap, {ID: id}));
    var rv = new RedreamVideo( '#' + id, url );
    loaded_video.push( url );
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
