;(function($){

    var nodeTable = function(el) {
        el.table = this;
        this.node = el;

        this.rows = new Array();
        this.selected_rows = new Array();

        var tableObj = this;
        var wrapper = this.node;
        $(wrapper).on('click', 'table.jstable > tbody > tr', function(){
            var index = $(this).attr('id');
            if (tableObj.options.multi_select) {
                // multi select.
                if ($(this).hasClass('active')){
                    $(this).removeClass('active');
                    tableObj.selected_rows.splice(
                        $.inArray(tableObj.rows[index], tableObj.selected_rows), 1  //have more better method?
                    );
                } else {
                    $(this).addClass('active');
                    tableObj.selected_rows.push(tableObj.rows[index]);
                }
            } else {
                // single select.
                $(this).addClass('active');
                $(this).siblings().removeClass('active');
                tableObj.selected_rows.length = 0;
                tableObj.selected_rows.push(tableObj.rows[index]);
            }
            $(wrapper).trigger('select', [tableObj, tableObj.selected_rows]);

        }).on('dblclick', 'table.jstable > tbody > tr', function(){
            var index = $(this).attr('id');
            var row_selected = tableObj.rows[index];
            $(wrapper).trigger('open', [tableObj, row_selected]);
        });
    };

    nodeTable.prototype = {
        show: function() {
            var header = this.options.source.header;
            var td_func = this.options.source.col;
            var table = $("<table class='jstable'></table>");
            var thead = $("<thead></thead>");
            var tbody = $("<tbody></tbody>");

            var head = $("<tr></tr>");
            if (header.length == 0){
                // default, show all cols.
                if (this.rows.length > 0) {
                    var row = this.rows[0];
                    for (var key in row) {
                        var th = $(`<th>${key}</th>`);
                        head.append(th);
                    }
                }
            } else {
                for (var i=0; i<header.length; i++) {
                    var th = $(`<th>${header[i]}</th>`);
                    head.append(th);
                }
            }

            thead.append(head);
            table.append(thead);

            for (var i=0; i<this.rows.length; i++) {
                var row = this.rows[i];
                var tr = $(`<tr id=${i}></tr>`);
                if (header.length == 0) {
                    // show all cols.
                    for (var key in row) {
                        var td_content = td_func(row[key], key, row);
                        var td = $(`<td>${td_content}</td>`);
                        tr.append(td);
                    }
                } else {
                    for (var j=0; j<header.length; j++) {
                        var key = header[j];
                        var td_content = td_func(row[key], key, row);
                        var td = $(`<td>${td_content}</td>`);
                        tr.append(td);                        
                    }
                }
                tbody.append(tr);
            }
            table.append(tbody);
            this.clear();
            $(this.node).append(table);
        },

        load: function(options) {
            var defaults = {
                multi_select: false,
                loading_timeout: 5,
                source: {
                    url:    '',
                    method: 'get',
                    data:   {},
                    header: [],
                    filter: function(data){
                        return data;
                    },
                    col: function(col_str, col_name, row){
                        return col_str;
                    },
                },
            };
            this.options = $.extend(true, defaults, options);

            var url = this.options.source.url;
            var type = this.options.source.method;
            var data = this.options.source.data;
            var timeout = this.options.loading_timeout * 1000;
            var _instance = this;
            if (url === '') {
                return;
            }
            this.clear();
            this.rows.length = 0;
            this.selected_rows.length = 0;
            this.loading();
            $.ajax({
                async:   true,
                type:    type,
                url:     url,
                data:    data,
                timeout: timeout,
                success: function(data){
                    var _fdata = _instance.options.source.filter(data);
                    _instance.rows = _fdata.slice(0);
                    _instance.show();
                },
                error: function(xhr, status, er){
                    alert('Error loading data or request timeout.');
                    _instance.clear();
                }
            });
        },

        clear: function() {
            $(this.node).empty();
        },

        loading: function() {
            var loading_img = $("<img class='loading'/>");
            $(this.node).append(loading_img);
        }
    };

    $.fn.jstable = function(options) {
        return this.each(function(){
            var table = new nodeTable(this);
            table.load(options);
        });
    }
}(jQuery));