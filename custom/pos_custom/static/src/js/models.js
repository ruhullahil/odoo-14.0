odoo.define('pos_custom.models',function(require) {
    "use strict";



var models = require('point_of_sale.models');
var gui = require('point_of_sale.Gui');
var core = require('web.core');
var QWeb = core.qweb;
var rpc = require('web.rpc');
var _t  = require('web.core')._t;
var session = require('web.session');

var exports = {};

models.load_models({
        model:  'product.product',
        fields: ['display_name', 'lst_price', 'standard_price', 'categ_id', 'pos_categ_id', 'taxes_id',
                 'barcode', 'default_code', 'to_weight', 'uom_id', 'description_sale', 'description',
                 'product_tmpl_id','tracking', 'write_date', 'available_in_pos', 'attribute_line_ids'],
        order:  _.map(['sequence','default_code','name'], function (name) { return {name: name}; }),
        domain: function(self){

            var domain = ['&', '&', ['sale_ok','=',true],['available_in_pos','=',true],'|',['company_id','=',self.config.company_id[0]],['company_id','=',false]];
            if (self.config.limit_categories &&  self.config.iface_available_categ_ids.length) {
                domain.unshift('&');
                domain.push(['pos_categ_id', 'in', self.config.iface_available_categ_ids]);
            }
            if (self.config.iface_tipproduct){
              domain.unshift(['id', '=', self.config.tip_product_id[0]]);
              domain.unshift('|');
            }
            return domain;
        },
        context: function(self){
//        console.log(self)
         return { display_default_code: false,
          location:self.config.default_location[0]};
         },
        loaded: function(self, products){
//        console.log(self)
            var using_company_currency = self.config.currency_id[0] === self.company.currency_id[0];
            var conversion_rate = self.currency.rate / self.company_currency.rate;
            self.db.add_products(_.map(products, function (product) {
//            console.log(product)
               var  product_qty = 0
                if (!using_company_currency) {
                    product.qty_available = product.with_context({location:self.config.default_location[0]}).qty_available
                    product.lst_price = round_pr(product.lst_price * conversion_rate, self.currency.rounding);
                }
                rpc
                    .query({
                        model: "product.product",
                        method: "get_product_qty_location",
                        args: [self.config.default_location[0]],
                        fields: [],

                    })
                    .then(function(produ) {
                    console.log(produ)
                        product_qty = produ
                    });
                product.qty_available  = product_qty
                product.categ = _.findWhere(self.product_categories, {'id': product.categ_id[0]});
                product.pos = self;
                return new exports.Product({}, product);
            }));
        },
    });
exports.Product = Backbone.Model.extend({
    initialize: function(attr, options){
        _.extend(this, options);
    },
    isAllowOnlyOneLot: function() {
        const productUnit = this.get_unit();
        return this.tracking === 'lot' || !productUnit || !productUnit.is_pos_groupable;
    },
    get_unit: function() {
        var unit_id = this.uom_id;
        if(!unit_id){
            return undefined;
        }
        unit_id = unit_id[0];
        if(!this.pos){
            return undefined;
        }
        return this.pos.units_by_id[unit_id];
    },


    get_product_qty: function() {
    console.log(this.pos)
        var qty_available = this.qty_available;
        if(!qty_available){
            return undefined;
        }

        if(!this.pos){
            return undefined;
        }
        return qty_available
    },
    // Port of get_product_price on product.pricelist.
    //
    // Anything related to UOM can be ignored, the POS will always use
    // the default UOM set on the product and the user cannot change
    // it.
    //
    // Pricelist items do not have to be sorted. All
    // product.pricelist.item records are loaded with a search_read
    // and were automatically sorted based on their _order by the
    // ORM. After that they are added in this order to the pricelists.
    get_price: function(pricelist, quantity, price_extra){
        var self = this;
        var date = moment();

        // In case of nested pricelists, it is necessary that all pricelists are made available in
        // the POS. Display a basic alert to the user in this case.
        if (pricelist === undefined) {
            alert(_t(
                'An error occurred when loading product prices. ' +
                'Make sure all pricelists are available in the POS.'
            ));
        }

        var category_ids = [];
        var category = this.categ;
        while (category) {
            category_ids.push(category.id);
            category = category.parent;
        }

        var pricelist_items = _.filter(pricelist.items, function (item) {
            return (! item.product_tmpl_id || item.product_tmpl_id[0] === self.product_tmpl_id) &&
                   (! item.product_id || item.product_id[0] === self.id) &&
                   (! item.categ_id || _.contains(category_ids, item.categ_id[0])) &&
                   (! item.date_start || moment(item.date_start).isSameOrBefore(date)) &&
                   (! item.date_end || moment(item.date_end).isSameOrAfter(date));
        });

        var price = self.lst_price;
        if (price_extra){
            price += price_extra;
        }
        _.find(pricelist_items, function (rule) {
            if (rule.min_quantity && quantity < rule.min_quantity) {
                return false;
            }

            if (rule.base === 'pricelist') {
                price = self.get_price(rule.base_pricelist, quantity);
            } else if (rule.base === 'standard_price') {
                price = self.standard_price;
            }

            if (rule.compute_price === 'fixed') {
                price = rule.fixed_price;
                return true;
            } else if (rule.compute_price === 'percentage') {
                price = price - (price * (rule.percent_price / 100));
                return true;
            } else {
                var price_limit = price;
                price = price - (price * (rule.price_discount / 100));
                if (rule.price_round) {
                    price = round_pr(price, rule.price_round);
                }
                if (rule.price_surcharge) {
                    price += rule.price_surcharge;
                }
                if (rule.price_min_margin) {
                    price = Math.max(price, price_limit + rule.price_min_margin);
                }
                if (rule.price_max_margin) {
                    price = Math.min(price, price_limit + rule.price_max_margin);
                }
                return true;
            }

            return false;
        });

        // This return value has to be rounded with round_di before
        // being used further. Note that this cannot happen here,
        // because it would cause inconsistencies with the backend for
        // pricelist that have base == 'pricelist'.
        return price;
    },
});
//    {
//    model: 'pos.order.line',
//    fields: ['product_id','qty','price_unit','price_subtotal_incl','order_id','discount','returned_qty'],
//    loaded: function(self,order_lines){
//
//    self.order_line = [];
//    for (var i = 0; i < order_lines.length; i++) {
//        self.order_line[i] = order_lines[i];
//    }
//    }
//});








var _super_orderline = models.Orderline;
models.Orderline = models.Orderline.extend({

    set_line_id: function(line_id){
        this.line_id = line_id;
    },
    export_as_JSON: function(){
        var json = _super_orderline.prototype.export_as_JSON.apply(this,arguments);
        json.line_id = this.line_id;
        return json;
    },
    init_from_JSON: function(json){
        _super_orderline.prototype.init_from_JSON.apply(this,arguments);
        this.line_id = json.line_id;
    },
});

var _super = models.Order;
models.Order = models.Order.extend({

    add_product: function (product, options) {


        var order    = this.pos.get_order();
        _super.prototype.add_product.call(this, product, options);
        if (options !== undefined) {
            if (options.extras !== undefined) {
                for (var prop in options.extras) {
                    if (prop === 'return_ref') {
                        this.return_ref = options.extras['return_ref']
                        this.trigger('change', this);
                    }
                    if (prop === 'label') {
                        order.selected_orderline.set_line_id(options.extras['label']);
                    }

                }

            }

        }

    },

    export_as_JSON: function(){
        var json = _super.prototype.export_as_JSON.apply(this,arguments);
        json.return_ref = this.return_ref;
        return json;
    },
    init_from_JSON: function(json){
        _super.prototype.init_from_JSON.apply(this,arguments);
        this.return_ref = json.return_ref;
    }

});

models.PosModel.extend({
    _save_to_server: function (orders, options) {
        if (!orders || !orders.length) {
            var result = $.Deferred();
            result.resolve([]);
            return result;
        }
        var fields = _.find(this.models,function(model){ return model.model === 'pos.order'; }).fields;
        options = options || {};

        var self = this;
        var timeout = typeof options.timeout === 'number' ? options.timeout : 7500 * orders.length;

        // Keep the order ids that are about to be sent to the
        // backend. In between create_from_ui and the success callback
        // new orders may have been added to it.
        var order_ids_to_sync = _.pluck(orders, 'id');

        // we try to send the order. shadow prevents a spinner if it takes too long. (unless we are sending an invoice,
        // then we want to notify the user that we are waiting on something )
        var args = [_.map(orders, function (order) {
                order.to_invoice = options.to_invoice || false;
                return order;
            })];
        return rpc.query({
                model: 'pos.order',
                method: 'create_from_ui',
                args: args,
                kwargs: {context: session.user_context},
            }, {
                timeout: timeout,
                shadow: !options.to_invoice
            })
            .then(function (server_ids) {
                _.each(order_ids_to_sync, function (order_id) {
                    self.db.remove_order(order_id);
                });
                self.set('failed',false);
                if (server_ids.length != 0){
                    for (var item in server_ids){
                        rpc.query({
                            model: 'pos.order',
                            method: 'search_read',
                            args: [[['id', '=', server_ids[item]]], fields],
                            limit: 1,
                        })
                        .then(function (order){
                            self.orders.unshift(order[0]);
                        });
                    }
                }
                self.load_server_data();
                return server_ids;
            }).catch(function (type, error){
                if(error.code === 200 ){    // Business Logic Error, not a connection problem
                    //if warning do not need to display traceback!!
                    if (error.data.exception_type == 'warning') {
                        delete error.data.debug;
                    }

                    // Hide error if already shown before ...
                    if ((!self.get('failed') || options.show_error) && !options.to_invoice) {
                        this.showpopup('error-traceback',{
                            'title': error.data.message,
                            'body':  error.data.debug
                        });
                    }
                    self.set('failed',error);
                }
                console.error('Failed to send orders:', orders);
            });
    },
});





});