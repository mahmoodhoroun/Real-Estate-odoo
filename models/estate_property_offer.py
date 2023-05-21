from odoo import fields, models,api
from datetime import datetime, timedelta
from odoo.exceptions import UserError , ValidationError




class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        string='Status',
        selection=[('Accepted', 'Accepted'), ('Refused', 'Refused')],
        help="Select the States",
        copy=False,
        defult="Accepted"
    )
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline" ,store=True)

    partner_id = fields.Many2one("res.partner",required=True)
    property_id = fields.Many2one("estate.property",required=True)
    property_type_id = fields.Many2one('estate.property.type', string='Property Type', related='property_id.property_type_id', store=True)

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline =  record.create_date + timedelta(days=record.validity)
            else:
                record.date_deadline =  fields.datetime.now() + timedelta(days=record.validity)
            
    @api.depends("date_deadline")
    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - record.create_date.date()).days
    
    def action_Accept(self):
        if not self.property_id.buyer_id:
            self.status = "Accepted"
            self.property_id.selling_price = self.price
            self.property_id.buyer_id = self.partner_id
            self.property_id.states1 = "Offer Accepted"
        else:
             raise UserError("You have accepted offer")

        
    def action_Refuse(self):
        if self.status == "Accepted":
            self.status = "Refused"
            self.property_id.selling_price = 0
            self.property_id.buyer_id = ""
        else:
            self.status = "Refused"

    _sql_constraints = [
        ('check_price', 'CHECK(price >= 0)','The Price must be positive')
    ]

    @api.model
    def create(self, values):
        property_id = values.get('property_id')
        price = values.get('price')

        # Check if the offer amount is lower than existing offers
        existing_offers = self.search([('property_id', '=', property_id)])
        if existing_offers and price < max(existing_offers.mapped('price')):
            raise ValidationError("The offer amount cannot be lower than an existing offer.")

        # Set the property state to 'Offer Received'
        property = self.env['estate.property'].browse(property_id)
        property.write({'states1': 'Offer Received'})

        return super(EstatePropertyOffer, self).create(values)
