odoo.define('erp2_custom.InheritCustomer', function(require) {
    'use strict';

    const { debounce } = owl.utils;
    const PosComponent = require('point_of_sale.PosComponent');
//    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const Chrome = require('point_of_sale.Chrome')
    const Registries = require('point_of_sale.Registries')
    const Gui = require('point_of_sale.Gui')

    const ClientListScreenInherit = (ClientListScreen) =>
    class extends ClientListScreen {

    async saveChanges(event) {
    console.log(event.detail.processedChanges)
    this.env.pos.custom_db.sync_partner()
            try {
                let partnerId = await this.rpc({
                    model: 'res.partner',
                    method: 'create_from_ui',
                    args: [event.detail.processedChanges],
                });
                await this.env.pos.load_new_partners();
                this.state.selectedClient = this.env.pos.db.get_partner_by_id(partnerId);
                this.state.detailIsShown = false;
                this.render();
            } catch (error) {
                if (error.message.code < 0) {
                var customer = event.detail.processedChanges
                customer.id = 1000001
                var lst_customer = [customer]
                this.env.pos.custom_db.need_to_update_partner(customer)
                await this.env.pos.db.add_partners(lst_customer);
                this.state.selectedClient = this.env.pos.db.get_partner_by_id(customer.id);
                this.state.detailIsShown = false;
                this.render();


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

    Registries.Component.extend(ClientListScreen, ClientListScreenInherit);
   return ClientListScreen;
    });