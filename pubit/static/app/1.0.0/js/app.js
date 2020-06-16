/*
 * tableNav
 * ==============================================
 * tableNav class manage tree, table, and navgation path.
 */
var tableNav = function(uuid, table, tree, btn_back, node_path_nav) {
    this.uuid = uuid;
    this.table = table;
    this.tree = tree;
    this.btn_back = btn_back;
    this.node_path_nav = node_path_nav;

    this.id_stack = new Array();
    this.id_stack.push('|');
    this._update_nav_path('|');
    this.btn_back.attr('disabled', true);
}

tableNav.prototype._update_nav_path = function(id) {
    var id_arr = id.split('|');
    if (id_arr.length == 2 && id_arr[1] == '') {
        delete id_arr[0];
    }
    var breadcrumb = $("<ol class='breadcrumb'></ol>");
    for (i=0; i<id_arr.length; i++) {
        var li = $('<li></li>');
        if(i==0) {
            // root path named 'Home'.
            var href = $("<a name='path-link' id='|' href='javascript:void(0);'>Home</a>");
        } else {
            var node_id = '';
            for (j=1; j<=i; j++) {
                node_id = node_id + '|' + id_arr[j];
            }
            var href = $("<a name='path-link' id='" + node_id + "' href='javascript:void(0);'>" + id_arr[i] + "</a>");
        }
        li.append(href);
        breadcrumb.append(li);
    }
    this.node_path_nav.empty();
    this.node_path_nav.append(breadcrumb);
}

tableNav.prototype.nav_go = function(id) {
    this.id_stack.push(id);
    this._update_nav_path(id);
    this.table.load({
        source: {
            url:    `/api/pub/${this.uuid}/${id}`,
            header: ['name', 'type', 'create', 'size'],
            filter: function(data){
                return data.children;
            },
        },
    });

    var tree = this.tree;
    tree.jstree('open_node', id, function() {
        tree.jstree('deselect_all', true);
        tree.jstree('select_node', id, true);
    });

    this.btn_back.attr('disabled', false);
}

tableNav.prototype.nav_back = function() {
    if (this.id_stack.length > 1) {
        this.id_stack.pop();    // pop current page.
        var id = this.id_stack[this.id_stack.length - 1];   // id = id_stack.top()
        this._update_nav_path(id);
        this.table.load({
            source: {
                url:    `/api/pub/${this.uuid}/${id}`,
                header: ['name', 'type', 'create', 'size'],
                filter: function(data){
                    return data.children;
                },
            },
        });
        if (this.id_stack.length == 1) {
            this.btn_back.attr('disabled', true);
        }
    }
}

tableNav.prototype.refresh = function() {
    var id = this.id_stack[this.id_stack.length - 1];   // id = id_stack.top();
    /* 
     * Refresh node trigger 'changed.jstree' event,
     * the event catch call nav_go() to load table,
     * so don't need load table again.
     */
    this.tree.jstree('refresh_node', id, true);  
}

tableNav.prototype.current_id = function() {
    return this.id_stack[this.id_stack.length - 1];
}

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