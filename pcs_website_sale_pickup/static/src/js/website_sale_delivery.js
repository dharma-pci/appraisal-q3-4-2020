odoo.define('pcs_website_sale_pickup.website_sale_delivery', function (require) {
    'use strict';
    
    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var _t = core._t;
    var concurrency = require('web.concurrency');
    var dp = new concurrency.DropPrevious();

    require('website_sale_delivery.checkout');

    publicWidget.registry.websiteSaleDelivery.include({
        // Function to send input shipping method by checked to python function show all active warehouse
        _onCarrierClick: function (ev) {
            var $radio = $(ev.currentTarget).find('input[type="radio"]');
            this._showLoading($radio);
            $radio.prop("checked", true);
            var $payButton = $('#o_payment_form_pay');
            $payButton.prop('disabled', true);
            if ($('#delivery_1')[0].checked == false) {
                    $payButton.enable();
                }
            if ($radio.val() == 1){
                dp.add(this._rpc({
                route: '/shop/list_warehouse',
                params: {
                    carrier_id: $radio.val(),
                },
                })).then(this._handleCarrierUpdateResult.bind(this));
            }
        },

        /*
            Function to send data choosed location to python function with route /shop/check_stock
            with return from python function ready to pick when available and when not will show alert message
            - when product ready to pickup (available stock in location) also enable pay button
            - when not ready will show alert message with custom text and disable pay button
        */

        _handleCarrierUpdateResult: function (result) {
            this._handleCarrierUpdateResultBadge(result);
            var $radio = $('#delivery_1');
            $radio.prop("checked", true);
            if($('#warehouse_location').length > 0){
                var warehouse_choose = $('.warehouse_id').val();
                dp.add(this._rpc({
                route: '/shop/check_stock',
                params: {
                    warehouse_id: warehouse_choose,
                    carrier_id: $radio.val(),
                },
                })).then(function(result) {
                    var $payButton = $('#o_payment_form_pay');
                    if (result){
                        if (result.ready_to_pick == false) {
                            alert(result.message_alert)
                            $payButton.prop('disabled', true);
                        } else {
                            $payButton.enable();
                        }
                    }
                });
            }
            else {
                $('#o_payment_form_pay').prop('disabled', true);
            }
            $.each(result.warehouse_id, function( index, value ) {
                option += "<option value='"+value.id+"'>"+value.name+"</option>"
            });
            if(result.personal_pickup != ''){
                if(result.warehouse_id.length > 0){
                    var option = '<option value=""> Select Location </option>'
                    $.each(result.warehouse_id, function( index, value ) {
                        option += "<option value='"+value.id+"'>"+value.name+"</option>"
                    });
                    var select_warehouse = "<select name='warehouse_id' class='form-control warehouse_id' id='warehouse_location'>"+option+"</select>";
                    if($('.warehouse_id').length < 1){
                        $('.o_delivery_carrier_select').first().append(select_warehouse); 
                    }
                }
            }
        },
    });
});
    