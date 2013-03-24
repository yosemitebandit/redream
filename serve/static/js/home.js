(function () {

var init = function () {
  var onTextareaKeyup = function (ev) {
    if (13 === ev.which) {
      $('#home-textarea').off('keyup', onTextareaKeyup);
      $('#large-circle-form').submit();
    }
  };
  $('#home-textarea').on('keyup', onTextareaKeyup);
};

$(init);

})();

$(function() {
    $('textarea').focus();
});
