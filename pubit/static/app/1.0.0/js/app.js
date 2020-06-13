/*
 * NodeTable: load nodes data and show it.
 * Usage:
 * =======================================
 * 1. Create global NodeTable object.
 * nodetab = new NodeTable(uuid);
 * 2. In function call load().
 * nodetab.load('/);
 * 3. Add 'path-link' href listener.
 * $("a[name='path-link']").on('click', function(){
 *      var path = $(this).attr('path);
 *      nodetab.load(path);
 * });
 */

var NodeTable = function(uuid) {
    this.uuid = uuid;
    this.id_stack = new Array();
};

NodeTable.prototype.selector_pub_path = "div[name='pub-path']";
NodeTable.prototype.selector_pub_nodes = "div[name='pub-nodes']";
NodeTable.prototype.selector_button_back = "a[name='nav-back']";

NodeTable.prototype.update_pub_path = function(id) {
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
    $(this.selector_pub_path).empty();
    $(this.selector_pub_path).append(breadcrumb);
};

NodeTable.prototype.show = function(nodes, style) {
    /*
     * style = 0 (default.): show column: name, type, create time, size.
     * style = 1 (for show search result.): show directory, name, type, create_time, size.
     */
    style = style || 0;
    var uuid = this.uuid;

    var table = $("<div class='table-nodes' uuid='" + uuid + "'></div>");

    var tab_head = $("<div class='table-nodes-head'></div>");
    var tab_head_row = $("<div class='table-nodes-row'></div>");
    
    var dir_head = $("<div class='table-nodes-col'>Directory</div>");
    var name_head = $("<div class='table-nodes-col'>Name</div>");
    var type_head = $("<div class='table-nodes-col'>Type</div>");
    var create_head = $("<div class='table-nodes-col'>Create time</div>");
    var size_head = $("<div class='table-nodes-col'>Size</div>");

    if (style == 1) {
        tab_head_row.append(dir_head);
    }

    tab_head_row.append(name_head);
    tab_head_row.append(type_head);
    tab_head_row.append(create_head);
    tab_head_row.append(size_head);

    tab_head.append(tab_head_row);
    table.append(tab_head);

    var tab_body = $("<div class='table-nodes-body'></div>");
    for (i=0; i<nodes.length; i++) {
        var node_id = nodes[i].id;
        var path = nodes[i].path;
        var node_type = nodes[i].type.toLowerCase();
        var node_name = nodes[i].name;

        var item_class = 'table-nodes-row';
        if (i == 0) {
            item_class = 'table-nodes-row active';
        }

        var item = $("<div class='" + item_class + "' id='" + node_id + "' type='" + node_type + "' uuid='" + uuid + "' path='" + path + "' name='" + node_name + "'></div>");
        var directory = $("<div class='table-nodes-col'>" + "<a name='path-link' href='javascript:void(0);' id='" + nodes[i].parent_id + "' name='parent-path'>" + nodes[i].parent_path + "</a>" + "</div>");
        var name = $("<div class='table-nodes-col'>" + nodes[i].name + "</div>");
        var type=$("<div class='table-nodes-col'>" + nodes[i].type + "</div>");
        var create = $("<div class='table-nodes-col'>" + nodes[i].create + "</div>");
        var size = $("<div class='table-nodes-col'>" + nodes[i].size + "</div>");
        
        if (style == 1) {
            item.append(directory);
        }

        item.append(name);
        item.append(type);
        item.append(create);
        item.append(size);
        tab_body.append(item);
    }
    table.append(tab_body);
    $(this.selector_pub_nodes).empty();
    $(this.selector_pub_nodes).append(table);
};

NodeTable.prototype.load = function(id) {
    this.update_pub_path(id);
    var ndtab_obj = this;
    var show_nodes = function(nodes, obj) {
        obj.show(nodes);
    };
    $.get(
        `/api/pub/${this.uuid}/${id}`,
        function(data){
            var nodes = data.children;
            console.log(nodes);
            show_nodes(nodes, ndtab_obj);
        }, 
        "json"
    );
    
    this.id_stack.push(id);

    if (this.id_stack.length<2) {
        $(this.selector_button_back).addClass('disabled');
    } else {
        $(this.selector_button_back).removeClass('disabled');
    }
};

NodeTable.prototype.current_id = function() {
    return this.id_stack[this.id_stack.length - 1];
}

NodeTable.prototype.reload = function() {
    var id = this.current_id();
    this.update_pub_path(id);
    var ndtab_obj = this;
    var show_nodes = function(nodes, obj) {
        obj.show(nodes);
    };
    $.get(
        `/api/pub/${this.uuid}/${id}`,
        function(data){
            var nodes = data.children;
            show_nodes(nodes, ndtab_obj);
        }, 
        "json"
    );
};

NodeTable.prototype.nav_back = function() {
    if (this.id_stack.length >= 2) {
        this.id_stack.pop();    // current page.
        var id = this.id_stack.pop();
        this.load(id);
    }
};

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