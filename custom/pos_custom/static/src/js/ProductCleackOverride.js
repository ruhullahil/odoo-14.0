odoo.define('pos_custom.ProductClickInherit', function(require) {
   'use strict';
   const PosComponent = require('point_of_sale.PosComponent');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { useState } = owl.hooks;
    const { parse } = require('web.field_utils');
   const ProductScreen = require('point_of_sale.ProductScreen');
   const { posbus } = require('point_of_sale.utils');
   const ProductScreenInherit = (ProductScreen) =>
            class extends ProductScreen {
               async _clickProduct(event) {
//               const screen = order.get_screen_data();
//               console.log(event)
               if (!this.currentOrder) {
                this.env.pos.add_new_order();
            }
            const product = event.detail;
            const options = await this._getAddProductOptions(product);
            console.log(options)
            // Do not add product if options is undefined.
            if (!options) return;
            // Add the product after having the extra information.
            this.currentOrder.add_product(product, options);
            NumberBuffer.reset();

            //   if (['ProductScreen', 'PaymentScreen'].includes(screen.name) && order.get_orderlines().length > 0) {
            //       const { confirmed } = await this.showPopup('ConfirmPopup', {
            //           title: 'Existing orderlines',
            //           body: `${order.name} has total amount of ${this.getTotal(
            //               order
            //           )}, are you sure you want delete this order?`,
            //       });
            //       if (!confirmed) return;
            //   }
            //   if (order) {
            //       order.destroy({ reason: 'abandon' });
            //   }
            //   posbus.trigger('order-deleted');
            }
            };
   Registries.Component.extend(ProductScreen, ProductScreenInherit);
   return ProductScreen;
            });