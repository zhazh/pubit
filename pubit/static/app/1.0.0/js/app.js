$(document).ready(function(){
    // Set modal box position when appeared.
	$("div.modal").on('show.bs.modal', function(e){
		var $this = $(this);
		var $modal_dialog = $this.find('.modal-dialog');
		$this.css('display', 'block');
		$modal_dialog.css({'margin-top': Math.max(0, ($(window).height() - $modal_dialog.height()) / 2) });
	});

    // ajax csrf protect.
    // html header include <meta name="csrf-token" content="{{csrf_token()}}">
    var csrftoken = $('meta[name=csrf-token]').attr('content');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $.ajaxSetup({
        // catch and handle ajax method exception.
        error: function(jqXHR, status, error){
			resp = JSON.parse(jqXHR.responseText);
            if (jqXHR.status===403 && resp.code===1) {
				alert('Admin unauthorized!');
				window.location = '/admin/login';
				return;
			}
			alert(resp.msg);
        }
    });
});