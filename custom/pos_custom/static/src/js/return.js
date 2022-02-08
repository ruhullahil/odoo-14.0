odoo.define('pos_custom.return',function(require) {
    "use strict";


var models = require('point_of_sale.models');
var gui = require('point_of_sale.Gui');
var core = require('web.core');
var QWeb = core.qweb;
var rpc = require('web.rpc');
var _t  = require('web.core')._t;
var session = require('web.session');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductItem');
    const { useListener } = require('web.custom_hooks');
    const { useState, useRef } = owl.hooks;
    const OrderManagementScreen = require('point_of_sale.OrderManagementScreen');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');



class ProductQty extends PosComponent {

       get product_qty() {
//       console.log(this.env.pos.config.default_location[0])
       var formattedUnitPrice = 0
      rpc
                  .query({
                      model: "product.product",
                       method: "get_product_qty_location",
                       args: [this.env.pos.config.default_location[0]],
                       fields: [],

                   })
                    .then(function(products) {
//                   console.log(products)
                        formattedUnitPrice = products
                    });

//            console.log(formattedUnitPrice)
                if ( ! formattedUnitPrice){
                return 0
                }
                return formattedUnitPrice
        }

}


ProductQty.template = 'ProductQty';
Registries.Component.add(ProductQty);


 return ProductQty;



});