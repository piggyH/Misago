// Misago modal controller
(function($) {

  var MisagoModal = function() {

    var _this = this;

    this.$modal = $('#ajax-modal');
    this.$content = $('#ajax-modal .modal-content');

    this.is_visible = function() {
      return $('body').hasClass('modal-open');
    }

    this.show = function(html) {
      if (_this.is_visible()) {
        _this.$content.fadeOut(200);
        _this.$content.html(html);
        _this.$content.fadeIn(200);
      } else {
        _this.$content.html(html);
        _this.$modal.modal({show: true});
      }
    }

    this.post = function(url, data) {
      $.post(url, data, function(data) {
        _this.show(data);
        Misago.DOM.changed();
      });
    }

  };

  Misago.Modal = new MisagoModal();

}(jQuery));
