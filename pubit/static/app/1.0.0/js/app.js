$(document).ready(function(){
    // Set modal box position when appeared.
	$("div.modal").on('show.bs.modal', function(e){
		var $this = $(this);
		var $modal_dialog = $this.find('.modal-dialog');
		$this.css('display', 'block');
		$modal_dialog.css({'margin-top': Math.max(0, ($(window).height() - $modal_dialog.height()) / 2) });
	});
});