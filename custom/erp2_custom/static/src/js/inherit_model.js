odoo.define("erp2_custom.PosModel", function(require) {
    "use strict";

    var rpc = require("web.rpc");
    var models = require("point_of_sale.models");
    var field_utils = require("web.field_utils");
    var newDb = require('erp2_custom.InheritDb')

    models.load_fields("product.product", ["qty_available", "type"]);

    var PosModelSuper = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        get_product_model: function() {
            return _.find(this.models, function(model) {
                return model.model === "product.product";
            });
        },
        initialize: function(session, attributes) {
            // Compatibility with pos_cache module
            // preserve product.product model data for future request
            this.product_product_model = this.get_product_model(this.models);
            this.custom_db = new newDb();
            PosModelSuper.initialize.apply(this, arguments);
        },
        load_server_data: function() {
            // Compatibility with pos_cache module
            var self = this;

            var loaded = PosModelSuper.load_server_data.call(this);
            if (this.get_product_model(this.models)) {
                return loaded;
            }
            // If product.product model is not presented in this.models after super was called then pos_cache module installed
            return loaded.then(function() {
                return rpc
                    .query({
                        model: "product.product",
                        method: "search_read",
                        args: [],
                        fields: ["qty_available", "type"],
                        domain: self.product_product_model.domain,
                        context: _.extend(self.product_product_model.context, {
                            location: self.config.default_location_src_id[0],
                        }),
                    })
                    .then(function(products) {
                        self.add_product_qty(products);
                    });
            });
        },
        set_product_qty_available: function(product, qty) {
            product.qty_available = qty;
            this.refresh_qty_available(product);
        },
        update_product_qty_from_order_lines: function(order) {
            var self = this;
            order.orderlines.each(function(line) {
                var product = line.get_product();
                product.qty_available = product.format_float_value(
                    product.qty_available - line.get_quantity(),
                    {digits: [69, 3]}
                );
                self.refresh_qty_available(product);
            });
            // Compatibility with pos_multi_session
            order.trigger("new_updates_to_send");
        },
        add_product_qty: function(products) {
            var self = this;
            _.each(products, function(p) {
                _.extend(self.db.get_product_by_id(p.id), p);
            });
        },
        refresh_qty_available: function(product) {
            var $elem = $("[data-product-id='" + product.id + "'] .qty-tag");
            $elem.html(product.rounded_qty());
            if (product.qty_available <= 0 && !$elem.hasClass("not-available")) {
                $elem.addClass("not-available");
            }
        },
        push_order: function(order, opts) {
            var pushed = PosModelSuper.push_order.call(this, order, opts);
            if (order) {
                this.update_product_qty_from_order_lines(order);
            }
            return pushed;
        },
        push_and_invoice_order: function(order) {
            var invoiced = PosModelSuper.push_and_invoice_order.call(this, order);

            if (order && order.get_client() && order.orderlines) {
                this.update_product_qty_from_order_lines(order);
            }

            return invoiced;
        },
    });

    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        export_as_JSON: function() {
            var data = OrderlineSuper.prototype.export_as_JSON.apply(this, arguments);
            data.qty_available = this.product.qty_available;
            return data;
        },
        // Compatibility with pos_multi_session
        apply_ms_data: function(data) {
            if (OrderlineSuper.prototype.apply_ms_data) {
                OrderlineSuper.prototype.apply_ms_data.apply(this, arguments);
            }
            var product = this.pos.db.get_product_by_id(data.product_id);
            if (product.qty_available !== data.qty_available) {
                this.pos.set_product_qty_available(product, data.qty_available);
            }
        },
    });

    models.Product = models.Product.extend({
        format_float_value: function(val) {
            var value = parseFloat(val);
            value = field_utils.format.float(value, {digits: [69, 3]});
            return String(parseFloat(value));
        },
        rounded_qty: function() {
        console.log(this)
            return this.format_float_value(this.qty_available);
        },
    });
});


//odoo.define('erp2_custom.modelsInherit', function (require) {
//"use strict";
//
//const CustomDb = require('erp2_custom.InheritDb')
//var models = require('point_of_sale.model')
//
//
//// The PosModel contains the Point Of Sale's representation of the backend.
//// Since the PoS must work in standalone ( Without connection to the server )
//// it must contains a representation of the server's PoS backend.
//// (taxes, product list, configuration options, etc.)  this representation
//// is fetched and stored by the PosModel at the initialisation.
//// this is done asynchronously, a ready deferred alows the GUI to wait interactively
//// for the loading to be completed
//// There is a single instance of the PosModel for each Front-End instance, it is usually called
//// 'pos' and is available to all widgets extending PosWidget.
//var posmodel_super = models.PosModel.prototype;
//models.PosModel = models.PosModel.extend({
////console.log('comming ')
//get_new_db: function(){
//console.log('custom db ins')
//this.custom_db = new CustomDb()
//return this;
//}
////initialize: function(attributes) {
////        posmodel_super.initialize.call(this, attributes);
////        this.custom_db = new  CustomDb();
////        console.log('this :',this)
////
//////        var  self = this;
//////        this.flush_mutex = new Mutex();                   // used to make sure the orders are sent to the server once at time
//////
//////        this.env = this.get('env');
//////        this.rpc = this.get('rpc');
//////        this.session = this.get('session');
//////        this.do_action = this.get('do_action');
//////        this.setLoadingMessage = this.get('setLoadingMessage');
//////        this.setLoadingProgress = this.get('setLoadingProgress');
//////        this.showLoadingSkip = this.get('showLoadingSkip');
//////
//////        this.proxy = new devices.ProxyDevice(this);              // used to communicate to the hardware devices via a local proxy
//////        this.barcode_reader = new BarcodeReader({'pos': this, proxy:this.proxy});
//////
//////        this.proxy_queue = new devices.JobQueue();           // used to prevent parallels communications to the proxy
//////        this.db = new PosDB();                       // a local database used to search trough products and categories & store pending orders
//////        this.debug = config.isDebug(); //debug mode
//////
//////        // Business data; loaded from the server at launch
//////        this.company_logo = null;
//////        this.company_logo_base64 = '';
//////        this.currency = null;
//////        this.company = null;
//////        this.user = null;
//////        this.users = [];
//////        this.employee = {name: null, id: null, barcode: null, user_id:null, pin:null};
//////        this.employees = [];
//////        this.partners = [];
//////        this.taxes = [];
//////        this.pos_session = null;
//////        this.config = null;
//////        this.units = [];
//////        this.units_by_id = {};
//////        this.uom_unit_id = null;
//////        this.default_pricelist = null;
//////        this.order_sequence = 1;
//////        window.posmodel = this;
//////
//////        // Object mapping the order's name (which contains the uid) to it's server_id after
//////        // validation (order paid then sent to the backend).
//////        this.validated_orders_name_server_id_map = {};
//////
//////        // Extract the config id from the url.
//////        var given_config = new RegExp('[\?&]config_id=([^&#]*)').exec(window.location.href);
//////        this.config_id = given_config && given_config[1] && parseInt(given_config[1]) || false;
//////
//////        // these dynamic attributes can be watched for change by other models or widgets
//////        this.set({
//////            'synch':            { status:'connected', pending:0 },
//////            'orders':           new OrderCollection(),
//////            'selectedOrder':    null,
//////            'selectedClient':   null,
//////            'cashier':          null,
//////            'selectedCategoryId': null,
//////        });
//////
//////        this.get('orders').on('remove', function(order,_unused_,options){
//////            self.on_removed_order(order,options.index,options.reason);
//////        });
//////
//////        // Forward the 'client' attribute on the selected order to 'selectedClient'
//////        function update_client() {
//////            var order = self.get_order();
//////            this.set('selectedClient', order ? order.get_client() : null );
//////        }
//////        this.get('orders').on('add remove change', update_client, this);
//////        this.on('change:selectedOrder', update_client, this);
//////
//////        // We fetch the backend data on the server asynchronously. this is done only when the pos user interface is launched,
//////        // Any change on this data made on the server is thus not reflected on the point of sale until it is relaunched.
//////        // when all the data has loaded, we compute some stuff, and declare the Pos ready to be used.
//////        this.ready = this.load_server_data().then(function(){
//////            return self.after_load_server_data();
//////        });
////    },
//
//});
//});