from odoo import fields, models,api
from datetime import datetime, timedelta
from odoo.exceptions import UserError , ValidationError

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _order = "id desc"

    name = fields.Char(required=True, string="Title")
    active_id = fields.Text(active=True)
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer")
    sales_person = fields.Many2one("res.users", string="Salesperson")
    tag_ids = fields.Many2many("estate.property.tag",options="{'color_picker': True}")
    offer_ids = fields.One2many("estate.property.offer","property_id")
    user_id = fields.Many2one('res.users',compute='_compute_user_id', string='User')


    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False,default=lambda self: fields.datetime.now() + timedelta(days=90))
    expected_price = fields.Float()
    selling_price = fields.Float(required=True,copy=False)
    bedrooms = fields.Integer(default=3)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    total_area = fields.Integer(compute="_compute_area", store=True)
    best_price = fields.Char(compute="_compute_best_price", store=True)
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[('North', 'North'), ('South', 'South'), ('East','East'),('Wast','Wast')],
        help="Select the Direction"
    )
    states1 = fields.Selection(
        string='State',
        selection=[('New', 'New'), ('Offer Received', 'Offer Received'), ('Offer Accepted','Offer Accepted'),('Sold','Sold'),('Canceled','Canceled')],
        help="Select the States",
        defult="new"
    )


    @api.depends("living_area", "garden_area")
    def _compute_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
            # raise UserError('Test test')
    
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            # raise UserError(record.offer_ids.price)
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0

    @api.onchange("garden")
    def _onchange_garden(self):
        # raise UserError(self.garden)
        if self.garden :
            self.garden_area = 10
            self.garden_orientation = "North"
        else:
            self.garden_area = 0
            self.garden_orientation = ""

    def action_cancel(self):
        for record in self:
            if record.states1 != "Sold":
                for record in self:
                    record.states1 = "Canceled"
            else:
                raise UserError("Sold proparites Cannot be Canceled")

    def action_sold(self):
        for record in self:
            if True:
                if record.states1 != "Canceled":
                    record.states1 = "Sold"
                else:
                    raise UserError("Canceled proparites Cannot be Sold")
            else:
                raise UserError("The proparity must be Offer Accepted")
    def create_invoice(self):
        pass

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Name must be unique.'),
        ('check_expected_price', 'CHECK(expected_price >= 0)','The Expected Price must be positive'),
        ('check_selling_price', 'CHECK(selling_price >= 0)','The Selling Price must be positive'),
        ]


    @api.constrains('selling_price','expected_price')
    def check_selling_price(self):
          for record in self:
                if record.offer_ids:
                    if record.selling_price < record.expected_price *0.9:
                        raise ValidationError("The the selling price cannot be lower than 90% of the expected price.")
    
    # @api.ondelete(at_uninstall=False)
    def unlink(self):
        if self.states1 == 'New' or self.states1 == 'Canceled':
            self.offer_ids.unlink()
            self.tag_ids.unlink()
            self.property_type_id.unlink()
            return super(EstateProperty,self).unlink()
        else:
            raise UserError('To be able to delete property it must be new or canceled')

    
    
    @api.model
    def create(self, values):
        values['states1'] = 'New'
        return super(EstateProperty, self).create(values)
    @api.depends('user_id')
    def _compute_user_id(self):
        for record in self:
            record.user_id = self.env.user