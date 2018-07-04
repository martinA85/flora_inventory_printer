from odoo import api, fields, models
import logging
import time

_logger = logging.getLogger(__name__)
class SockValuationReport(models.TransientModel):
    _name = 'report.stock_valuation_flora'
    _description = 'Sotck valuation report for floravert'

    @api.multi
    def generate_report(self, data):
        categ_dict = {}
        return self.env.ref('stock_printer.stock_valuation_report').report_action([], data=data)


class StockValuation(models.AbstractModel):

    _name="report.stock_printer.report_stock_valuation"
    @api.model 
    def get_products_ids(self):
        product_ids = self.env['product.template'].search([('qty_available','>',0)]).sorted(key=lambda r:r.categ_id.name)
        categ_dict = {}
        total = 0
        for product in product_ids:
            valuation = 0
            if(product.categ_id.name in categ_dict):
                valuation = product.standard_price * product.qty_available
                categ_dict[product.categ_id.name]['valuation'] = categ_dict[product.categ_id.name]['valuation'] + valuation
            else:
                categ_dict[product.categ_id.name] = {'categ_name':product.categ_id.name, 'valuation':product.standard_price * product.qty_available}
            total = total + product.standard_price * product.qty_available
        categ_lst = []
        for key in categ_dict:
            categ_lst.append({'name':categ_dict[key]['categ_name'],'value':categ_dict[key]['valuation']})

        return {
            'product_ids' : product_ids,
            'categ_value' : categ_lst,
            'total' : total
        }

    @api.model
    def get_data_inventory(self, data):
        inventory_id = data['active_id']
        inventory = self.env['stock.inventory'].browse(inventory_id)
        product_ids = []
        for line in inventory.line_ids:
            product_ids.append(line.product_id)
        categ_dict = {}
        total = 0
        for product in product_ids:
            valuation = 0
            if(product.categ_id.name in categ_dict):
                valuation = product.standard_price * product.qty_available
                categ_dict[product.categ_id.name]['valuation'] = categ_dict[product.categ_id.name]['valuation'] + valuation
            else:
                categ_dict[product.categ_id.name] = {'categ_name':product.categ_id.name, 'valuation':product.standard_price * product.qty_available}
            total = total + product.standard_price * product.qty_available
        categ_lst = []
        for key in categ_dict:
            categ_lst.append({'name':categ_dict[key]['categ_name'],'value':categ_dict[key]['valuation']})

        return {
            'product_ids' : product_ids,
            'categ_value' : categ_lst,
            'total' : total
        }


    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        start = time.time()
        if "active_model" in data:
            _logger.info("active_model")
            if data["active_model"] == "stock.inventory":
                data.update(self.get_data_inventory(data))
        else:
            data.update(self.get_products_ids())
        _logger.info(data)
        stop = time.time()
        return data
