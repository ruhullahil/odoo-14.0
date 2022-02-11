odoo.define('erp2_custom.InheritDb', function(require) {
    'use strict';
    var core = require('web.core');
    var utils = require('web.utils');
    var rpc = require('web.rpc');
    /* The PosDB holds reference to data that is either
     * - static: does not change between pos reloads
     * - persistent : must stay between reloads ( orders )
     */

    var PosDBInherit = core.Class.extend({
     name: 'openerp_pos_db', //the prefix of the localstorage data
    limit: 100,  // the maximum number of results returned by a search
    init: function(options){
        options = options || {};
        this.name = options.name || this.name;
        this.list_need_to_update = []

    },
    need_to_update_partner: function(customer){
        this.list_need_to_update.push(customer)
        },
    sync_partner: function(){
    var customers = this.list_need_to_update;
    for (var i = 0; customers.length;i++){
    var customer_t = customers[i]
                try {
                let partnerId = this.rpc({
                    model: 'res.partner',
                    method: 'create_from_ui',
                    args: [customer_t],
                });
//                this.env.pos.load_new_partners();
//                this.state.selectedClient = this.env.pos.db.get_partner_by_id(partnerId);
//                this.state.detailIsShown = false;
//                this.render();
            } catch (error) {
                if (error.message.code < 0) {
                var customer = customer_t
                customer.id = 1000001
                var lst_customer = [customer]
                this.env.pos.db.need_to_update_partner(customer)
                this.env.pos.db.add_partners(lst_customer);
//                this.state.selectedClient = this.env.pos.db.get_partner_by_id(customer.id);
//                this.state.detailIsShown = false;
//                this.render();


//                    await this.showPopup('OfflineErrorPopup', {
//                        title: this.env._t('Offline'),
//                        body: this.env._t('Unable to save changes.'),
//                    });
                } else {
                    throw error;
                }
            }
    }
    }

    });

    return PosDBInherit
    });

//    const InheritPosDb = (Db) =>{
//    add_partner: function(partner){
//        var updated_count = 0;
//        var new_write_date = '';
//        var partner;
//        for(var i = 0, len = partners.length; i < len; i++){
//            partner = partners[i];
//
//            var local_partner_date = (this.partner_write_date || '').replace(/^(\d{4}-\d{2}-\d{2}) ((\d{2}:?){3})$/, '$1T$2Z');
//            var dist_partner_date = (partner.write_date || '').replace(/^(\d{4}-\d{2}-\d{2}) ((\d{2}:?){3})$/, '$1T$2Z');
//            if (    this.partner_write_date &&
//                    this.partner_by_id[partner.id] &&
//                    new Date(local_partner_date).getTime() + 1000 >=
//                    new Date(dist_partner_date).getTime() ) {
//                // FIXME: The write_date is stored with milisec precision in the database
//                // but the dates we get back are only precise to the second. This means when
//                // you read partners modified strictly after time X, you get back partners that were
//                // modified X - 1 sec ago.
//                continue;
//            } else if ( new_write_date < partner.write_date ) {
//                new_write_date  = partner.write_date;
//            }
//            if (!this.partner_by_id[partner.id]) {
//                this.partner_sorted.push(partner.id);
//            }
//            this.partner_by_id[partner.id] = partner;
//
//            updated_count += 1;
//        }
//
//        this.partner_write_date = new_write_date || this.partner_write_date;
//
//        if (updated_count) {
//            // If there were updates, we need to completely
//            // rebuild the search string and the barcode indexing
//
//            this.partner_search_string = "";
//            this.partner_by_barcode = {};
//
//            for (var id in this.partner_by_id) {
//                partner = this.partner_by_id[id];
//
//                if(partner.barcode){
//                    this.partner_by_barcode[partner.barcode] = partner;
//                }
//                partner.address = (partner.street ? partner.street + ', ': '') +
//                                  (partner.zip ? partner.zip + ', ': '') +
//                                  (partner.city ? partner.city + ', ': '') +
//                                  (partner.state_id ? partner.state_id[1] + ', ': '') +
//                                  (partner.country_id ? partner.country_id[1]: '');
//                this.partner_search_string += this._partner_search_string(partner);
//            }
//
//            this.partner_search_string = utils.unaccent(this.partner_search_string);
//        }
//        return updated_count;
//    },
//    }
//    Registries.Component.extend(Db, InheritPosDb);
//   return Db;
