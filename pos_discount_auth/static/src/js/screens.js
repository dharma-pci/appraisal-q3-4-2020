odoo.define("pos_discount_auth.screens", function(require) {
    "use strict";

    var core = require("web.core");
    var screens = require("point_of_sale.screens");
    var gui = require('point_of_sale.gui');
    var rpc = require("web.rpc");
    var _t = core._t;

    screens.NumpadWidget.include({
        clickChangeMode: function(event) {
            var self = this;
            var cashier = this.pos.get('cashier') || this.pos.get_cashier();
            var newMode = event.currentTarget.attributes['data-mode'].nodeValue;
            if (cashier.role == 'manager'){
                return this.state.changeMode(newMode);
            }else{
                self.approval_pos_disc(newMode);
            }
        },
        // Function Approval discount if user is Pos user
        approval_pos_disc:function(newMode){
            // only use discount auth
            if (newMode != 'discount'){
                return this.state.changeMode(newMode);
            }
            var self = this;

            // get all pos manager users
            var list = [];
            this.pos.users.forEach(function(user) {
                if (user.role === 'manager') {
                    list.push({
                    'label': user.name,
                    'item':  user,
                    });
                }
            });

            // Function to choose approval manager
            self.pos.gui.show_popup('selection', {
                title:  _t('Select Manager'),
                list: list,
                confirm: function(user){
                    // Check Authentication trough rpc
                    // the idea causes pin manager couldn't access from cache
                    self.pos.gui.show_popup('password', {
                        confirm:function(password){
                            this._rpc({
                                model: 'res.users',
                                method: 'check_authentication',
                                args: [user.id, password]
                            }).then(function (login) {
                                if(login.login_status == 'Success'){
                                     if(self.pos.get_order().selected_orderline){
                                        self.pos.get_order().selected_orderline.set_approval_manager_in_orderline(user.id);
                                    }
                                    return self.state.changeMode(newMode)

                                }else{ 
                                    alert(login.login_status);
                                }   
                            }, function(err,event){
                                event.preventDefault();
                                self.gui.show_popup('error',{
                                    'title': _t('Error: Could not save changes'),
                                    'body': _t('Please Check Your internet connection'),
                                });
                            });
                        },
                        cancel:function(){
                            return self.approval_pos_disc()
                        }
                    });
                },
                is_selected: function (user) {
                    return user === self.pos.get_cashier();
                },
            });
        },
    });


    return screens;
});
