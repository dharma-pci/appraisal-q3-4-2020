odoo.define('pos_order_return.models', function (require) {
    "use strict";
    var models = require('point_of_sale.models');

    var _super_posorder = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            _super_posorder.initialize.apply(this, arguments);
            if (!this.pos_return_from) {
                this.pos_return_from = false;
            }
        },
        init_from_JSON: function (json) {
            var res = _super_posorder.init_from_JSON.apply(this, arguments);
            if (json.pos_return_from) {
                this.pos_return_from = json.pos_return_from;
            } else {
                this.pos_return_from = false;
            }
            return res
        },
        export_as_JSON: function () {
            var json = _super_posorder.export_as_JSON.apply(this, arguments);
            if (this.pos_return_from) {
                json.pos_return_from = this.get_pos_return_from();
            } else {
                json.pos_return_from = false;
            }
            return json
        },
        get_pos_return_from:function(){
            return this.pos_return_from
        },
        set_pos_return_from:function(value){
            var self = this;
            self.pos_return_from = value;
            this.trigger('change', this);
        },
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function() {
            _super_orderline.initialize.apply(this,arguments);
            if (!this.from_return_line_id) {
                this.from_return_line_id = false;
            }

        },
        init_from_JSON: function(json) {
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.from_return_line_id = json.from_return_line_id;
        },
        export_as_JSON: function() {
            var json = _super_orderline.export_as_JSON.apply(this,arguments);
            json.from_return_line_id = this.from_return_line_id;
            return json;
        },
        set_from_return_line_id:function(value){
            this.from_return_line_id = value;
            this.trigger('change', this);
        },
    });
});