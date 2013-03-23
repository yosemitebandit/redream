(function () {
  var background_jpg_width  = 2560;
  var background_jpg_height = 1600;
  var background_jpg_ratio = background_jpg_width / background_jpg_height;

  var handle_window_resize = null;
  var $window;
  var $body;
  var misec_resize = parseInt((1000/60), 10);

  var init = function () {
    $window = $(window);
    $body = $(document.body);
    $window.on('resize', onWindowResize);
    onWindowResizeImpl();
  };

  var onWindowResize = function (ev) {
    if (handle_window_resize) {
      clearTimeout(handle_window_resize);
    }
    handle_window_resize = setTimeout(onWindowResizeImpl, misec_resize);
  };

  var onWindowResizeImpl = function () {
    handle_window_resize = null;
    var r = $window.width() / $window.height();
    if (r > background_jpg_ratio) {
      $body.addClass('portrait-window');
    }
    else {
      $body.removeClass('portrait-window');
    }
  };

  $(init);
})();