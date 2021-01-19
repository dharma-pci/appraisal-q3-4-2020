odoo.define("pos_order_return.screens", function(require) {
    "use strict";

    var core = require("web.core");
    var qweb = core.qweb;
    var screens = require("point_of_sale.screens");
    var gui = require('point_of_sale.gui');
    var rpc = require("web.rpc");
    var _t = core._t;

    //register button action for show screen pos order screens 
    var OrderSearch = screens.ActionButtonWidget.extend({
        template: 'OrderSearch',

        init: function (parent, options) {
            this._super(parent, options);
        },
        button_click: function() {
            var self = this;
            this.pos.gui.show_screen('OrdersScreenWidget');
        },
        
    });
    screens.define_action_button({
        'name': 'OrderSearch',
        'widget': OrderSearch,
    });

    
    screens.ProductScreenWidget.include({
        // inherit start for copy all action click and button to html append button-list
        // then add class in control-buttons for hide
        start: function () {
            this._super();
            var action_buttons = this.action_buttons;
            for (var list in action_buttons) {
                action_buttons[list].appendTo(this.$('.button-list'));
            }
            this.$('.control-buttons').addClass('oe_hidden');
        },
    });
    // order screen view
    var OrdersScreenWidget = screens.ScreenWidget.extend({
        template: "OrdersScreenWidget",
        init: function(parent, options) {
            this._super(parent, options);
        },
        // in show declare all function button click in here
        // example add function keypres enter in searchbar
        // button return order
        show: function() {
            var self = this;
            this._super();
            this.$(".back").click(function() {
                self.gui.show_screen("products");
            });
            var search_timeout = null;
            this.$(".searchbox input").on("keypress", function(event) {
                clearTimeout(search_timeout);
                // so this will work or trigger function perform search when even enter is keypress
                // and has 3 length character
                var query = this.value;
                if (query.length >= 3 && event.which === 13){
                    search_timeout = setTimeout(function() {
                        self.perform_search(query, event.which === 13);
                    }, 70);
                }
            });
            //button click return 
            //after select order will go to pos order details
            this.$('.return_order').on("click", function(event){
                if (self.order_selected_id){
                    return rpc.query({
                        model: 'pos.order',
                        method: 'get_order_line_search',
                        args: [self.order_selected_id]
                    }).then(function(orderlines){
                        if (orderlines){
                            return self.pos.gui.show_popup('OrderDetails',{lines:orderlines})
                        }
                        else{
                            alert('no orderline')
                        }
                    })
                }
                else{
                    alert('order not selected')
                }
            })
            // delegate function click later if has orderline
            this.$(".order-list-contents").delegate(".order-line", "click", function(event){
                self.line_select(event, $(this), parseInt($(this).data('id')));
            });
        },
        // this function get order from searchbox input text
        // call rpc backend and then result do render list (render_pos_order_list)
        // if empty searchbox text will make it clear
        perform_search: function (query) {
            var self=this;
            if (query) {
                rpc.query({
                    model: 'pos.order',
                    method: 'get_order_search',
                    args:[query],
                }).then(function (orders) {
                    if (orders){
                        return self.render_pos_order_list(orders);
                    }else{
                        alert('order not found')
                    }
                });
            } else {
                // orders = this.pos.db.orders_store;
                return this.render_pos_order_list(false);
            }
            self.clear_search();
        },
        //after done perform_search will trigger clear function
        clear_search: function () {
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },
        // convert data time to appropritate time in js
        get_datetime_format: function(datetime) {
            var d = new Date(datetime);
            return new Date(
                d.getTime() - d.getTimezoneOffset() * 60000
            ).toLocaleString();
        },
        //this function is for render list of pos order
        render_pos_order_list: function (orders) {
            var contents = this.$el[0].querySelector('.order-list-contents');
            contents.innerHTML = "";
            if (orders){
                for (var i = 1, len = Math.min(orders.length, 1000); i <= len; i++) {
                    var order = orders[orders.length-i];
                    var pos_order_row_html = qweb.render('OrderHistory', {widget: this, order: order});
                    var pos_order_row = document.createElement('tbody');
                    pos_order_row.innerHTML = pos_order_row_html;
                    pos_order_row = pos_order_row.childNodes[1]; 
                    contents.appendChild(pos_order_row);
                }
            }
        },
        // if order list selected put data order id to var temp
        // then make it highlight 
        line_select: function(event, $line, id) {
            this.$('.order-line').removeClass('highlight');
            $line.addClass('highlight');
            this.order_selected_id = id;
        }
        
    });
    gui.define_screen({
        name: "OrdersScreenWidget",
        widget: OrdersScreenWidget,
    });



    return screens;
});