odoo.define('pos_order_return.popups', function (require) {
    "use strict";

    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var _t  = require('web.core')._t;

    var OrderDetails = PopupWidget.extend({
        template: 'OrderDetails',
        //show function will had paramater options to parse render element
        show: function(options){
            var self = this;
            options = options || {};
            this._super(options);

            this.lines = options.lines || [];
            this.renderElement();
        },
        renderElement: function(){
            this._super();
            var self = this;
            // add click funtion minus
            this.$('.qty_minus').click(function () {
                var line_id = parseInt($(this).data('id'));
                var quantity_now = parseFloat($(this).parent().find('.qty_'+String(line_id)).text());
                if ((quantity_now -1) >= 0) {
                    var new_quantity = quantity_now - 1;
                    $(this).parent().find('.qty_'+String(line_id)).text(new_quantity);
                }
            });
            //add click funtcion +
            this.$('.qty_plus').click(function () {
                var line_id = parseInt($(this).data('id'));
                var quantity = parseFloat($(this).parent().data('qty_def'));
                var quantity_now = parseFloat($(this).parent().find('.qty_'+String(line_id)).text());
                if ((quantity_now + 1) <= (quantity)) {
                    var new_quantity = quantity_now + 1;
                    $(this).parent().find('.qty_'+String(line_id)).text(new_quantity);
                }
            });
        },
        //popup when click confirm
        click_confirm: function(){
            var self=this;
            var list_data_return = self.convert_data_html_pos_return_line();
            self.pos.add_new_order();
            for (var index = 0; index < list_data_return.length; index++) {
                self.pos.get_order().add_product(self.pos.db.product_by_id[list_data_return[index].product_id],{quantity:(list_data_return[index].qty * -1)})
            }
            self.pos.gui.show_screen('payment');

        },
        // get data need for apply return order
        convert_data_html_pos_return_line:function(){
            var html_table = this.$('.order-line-details');
            var list_return = []
            for (var index = 0; index < html_table.length; index++) {
                var id_line = html_table[index].getAttribute('data-id')
                var qty = parseFloat(html_table.find('.qty_'+String(id_line)).text())
                if (qty > 0){
                    var id_product = html_table[index].getAttribute('data-product_id')
                    list_return.push({product_id:id_product,qty:qty});
                }   
            }
            return list_return
        }
    });
    gui.define_popup({name:'OrderDetails', widget: OrderDetails});
});