from odoo import models, fields, api

from odoo.exceptions import UserError


class PeriodReport(models.TransientModel):
    _name = "period.report"

    _description = 'Period Report'

    report_type = fields.Selection([
        ('sales', 'Sales (Period And Graph Report)'),
        ('purchase', 'Purchase (Period And Graph Report)'),
        ('expert', 'Expert Report'),
        ('customer', 'Customer Report'),
        ('arabic_gum_type', 'Arabic Gum Type Report'),
        ('inventory_of_tallying_product', 'Inventory Of Tallying Product Report'),
        ('goods_transport', 'Goods Transport Report'),
        ('returns', 'Returns Report'),
        ('commissioner', 'Commissioners Report'),
        ('producer', 'Producers Report'),
        ('warehouseman', 'Warehousemen Report'),
        ('employee', 'Employees Report'),
        ('supervisor', 'Supervisors Report'),
        ('driver', 'Drivers Report'),
        ('trucks', 'Trucks Report'),
        ('job', 'Jobs Report'),
        ('warehouse', 'Warehouses Report'),
        ('arabic_gum_price', 'Arabic Gum Prices Report'),
        ('raw_storage', 'Raw Storages Report'),
        ('purity_storage', 'Purity Storages Report'),
        ('procure_order', 'Procure Order Report'),
        ('order', 'Sale Orders Report'),
    ], string="Choos Report")

    date_from = fields.Date(string="Period From")
    date_to = fields.Date(string="To", default=fields.Datetime.now)




    def show_chart_report(self):
        action = False

        if self.report_type == 'sales':
            action = self.env.ref('boraush_trading.action_sales_graph').read()[0]
        elif self.report_type == 'purchase':
            action = self.env.ref('boraush_trading.action_purchases_graph').read()[0]
        else:
            raise UserError("There is No Graph Report To This Report Type")

        return action



    def print_period_report(self):
        if self.report_type == 'sales':
            sales = self.env['sale'].search([
                ('sale_date', '>=', self.date_from),
                ('sale_date', '<=', self.date_to)
            ])
            if not sales:
                raise UserError("No sales found in this period!")

            return self.env.ref('boraush_trading.sale_report').report_action(sales)




        elif self.report_type == 'purchase':
            purchases = self.env['purchase'].search([
                ('purchase_date', '>=', self.date_from),
                ('purchase_date', '<=', self.date_to)
            ])
            if not purchases:
                raise UserError("No purchases found in this period!")

            return self.env.ref('boraush_trading.purchase_report').report_action(purchases)

        elif self.report_type == 'expert':
            expert = self.env['expert'].search([
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ])
            if not expert:
                raise UserError("No experts found in this period!")

            return self.env.ref('boraush_trading.expert_report').report_action(expert)

        elif self.report_type == 'customer':
            customer = self.env['customer'].search([
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ])
            if not customer:
                raise UserError("No customers found in this period!")

            return self.env.ref('boraush_trading.customer_report').report_action(customer)


        elif self.report_type == 'arabic_gum_type':
            arabic_gum_type = self.env['arabic.gum.type'].search([
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to)
            ])
            if not arabic_gum_type:
                raise UserError("No arabic gum types found in this period!")

            return self.env.ref('boraush_trading.arabic_gum_type_report').report_action(arabic_gum_type)



        elif self.report_type == 'inventory_of_tallying_product':
            inventory_of_tallying_product = self.env['inventory.of.tallying.product'].search([
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to)
            ])
            if not inventory_of_tallying_product:
                raise UserError("No tallying products found in this period!")

            return self.env.ref('boraush_trading.inventory_tallying_product_report').report_action(inventory_of_tallying_product)



        elif self.report_type == 'goods_transport':
            goods_transport = self.env['goods.transport'].search([
                ('transport_date', '>=', self.date_from),
                ('transport_date', '<=', self.date_to)
            ])
            if not goods_transport:
                raise UserError("No goods transport  found in this period!")

            return self.env.ref('boraush_trading.goods_transport_report').report_action(goods_transport)


        elif self.report_type == 'returns':
            returns = self.env['returns'].search([
                ('return_date', '>=', self.date_from),
                ('return_date', '<=', self.date_to)
            ])
            if not returns:
                raise UserError("No returns found in this period!")

            return self.env.ref('boraush_trading.returns_report').report_action(returns)

        elif self.report_type == 'commissioner':
            commissioner = self.env['commissioner'].search([
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ])
            if not commissioner:
                raise UserError("No Commissioners found in this period!")

            return self.env.ref('boraush_trading.commissioner_report').report_action(commissioner)

        elif self.report_type == 'producer':
            producer = self.env['producer'].search([
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ])
            if not producer:
                raise UserError("No producers found in this period!")

            return self.env.ref('boraush_trading.producer_report').report_action(producer)

        elif self.report_type == 'warehouseman':
            warehouseman = self.env['warehouseman'].search([
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ])
            if not warehouseman:
                raise UserError("No warehousemans found in this period!")

            return self.env.ref('boraush_trading.warehouseman_report').report_action(warehouseman)

        elif self.report_type == 'employee':
            employee = self.env['employee'].search([
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ])
            if not employee:
                raise UserError("No employees found in this period!")

            return self.env.ref('boraush_trading.employee_report').report_action(employee)

        elif self.report_type == 'supervisor':
            supervisor = self.env['supervisor'].search([
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ])
            if not supervisor:
                raise UserError("No supervisors found in this period!")

            return self.env.ref('boraush_trading.supervisor_report').report_action(supervisor)

        elif self.report_type == 'driver':
            driver = self.env['driver'].search([
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ])
            if not driver:
                raise UserError("No drivers found in this period!")

            return self.env.ref('boraush_trading.driver_report').report_action(driver)

        elif self.report_type == 'trucks':
            trucks = self.env['trucks'].search([
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ])
            if not trucks:
                raise UserError("No trucks found in this period!")

            return self.env.ref('boraush_trading.trucks_report').report_action(trucks)

        elif self.report_type == 'job':
            job = self.env['job'].search([
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ])
            if not job:
                raise UserError("No jobs found in this period!")

            return self.env.ref('boraush_trading.job_report').report_action(job)

        elif self.report_type == 'warehouse':
            warehouse = self.env['warehouse'].search([
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ])
            if not warehouse:
                raise UserError("No warehouses found in this period!")

            return self.env.ref('boraush_trading.warehouse_report').report_action(warehouse)

        elif self.report_type == 'arabic_gum_price':
            arabic_gum_price = self.env['arabic.gum.price'].search([
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to)
            ])
            if not arabic_gum_price:
                raise UserError("No arabic gum prices found in this period!")

            return self.env.ref('boraush_trading.arabic_gum_price_report').report_action(arabic_gum_price)

        elif self.report_type == 'raw_storage':
            raw_storage = self.env['raw.storage'].search([
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ])
            if not raw_storage:
                raise UserError("No raw storage found in this period!")

            return self.env.ref('boraush_trading.raw_storage_report').report_action(raw_storage)

        elif self.report_type == 'purity_storage':
            purity_storage = self.env['purity.storage'].search([
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ])
            if not purity_storage:
                raise UserError("No purity storages found in this period!")

            return self.env.ref('boraush_trading.purity_storage_report').report_action(purity_storage)


        elif self.report_type == 'procure_order':
            procure_order = self.env['procure.order'].search([
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ])
            if not procure_order:
                raise UserError("No procure orders found in this period!")

            return self.env.ref('boraush_trading.procure_order_report').report_action(procure_order)


        elif self.report_type == 'order':
            order = self.env['order'].search([
                ('date_order', '>=', self.date_from),
                ('date_order', '<=', self.date_to)
            ])
            if not order:
                raise UserError("No sale orders found in this period!")

            return self.env.ref('boraush_trading.order_report').report_action(order)

        else:
            raise UserError("Report Type Not Implemented Yet")

