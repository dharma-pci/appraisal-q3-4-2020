/* Copyright 2017-2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
 * Copyright 2018 Artem Losev
 * Copyright 2018-2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License MIT (https://opensource.org/licenses/MIT). */
 odoo.define("pos_discount_auth.models", function(require) {
    "use strict";
    var models = require("point_of_sale.models");
    var rpc = require("web.rpc");

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function() {
            _super_orderline.initialize.apply(this,arguments);
            if (!this.manager_disc_approval) {
                this.manager_disc_approval = false;
            }
        },
        init_from_JSON: function(json) {
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.manager_disc_approval = json.manager_disc_approval;

        },
        export_as_JSON: function() {
            var json = _super_orderline.export_as_JSON.apply(this,arguments);
            json.manager_disc_approval = this.manager_disc_approval;
            return json;
        },
        set_approval_manager_in_orderline:function(value){
            this.manager_disc_approval = value;
            this.trigger('change', this);
        },
    });

});