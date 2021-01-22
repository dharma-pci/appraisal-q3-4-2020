from odoo.tests.common import TransactionCase
from odoo.exceptions import except_orm, UserError
import datetime


class TestMaterialRequest(TransactionCase):
    """ Test Material Request Creation"""

    def setUp(self):
        super(TestMaterialRequest, self).setUp()
        self.mrp_production = self.env['mrp.production']
        self.material_request = self.env['material.request']
        self.material_request_line = self.env['material.request.line']

        
        
    def test_mo_creation_result(self):
        now = datetime.datetime.now()
        test_product = self.env.ref('mrp.product_product_computer_desk_head')
        self.mo = self.mrp_production.create({
            'product_id':test_product.id,
            'product_uom_id': test_product.uom_id.id,
            'bom_id':test_product.bom_ids[0].id
        })
        """Test Raw Material empty"""
        self.assertEqual(0, len(self.mo.move_raw_ids),
                         'It should be 0')
        self.assertIsNotNone(self.mo.move_raw_ids)
        """ Test Material Request Created from MO"""
        self.assertIsNotNone(self.mo.material_request_id)
        """Test State Material Request State"""
        self.assertEqual('draft', self.mo.material_request_id.state,
                         'It should be draft')
        self.mo.material_request_id.action_confirm()
        self.assertEqual('confirm', self.mo.material_request_id.state,
                         'It should be confirm')
        self.mo.material_request_id.action_approve()
        self.assertEqual('done', self.mo.material_request_id.state,
                         'It should be done')
        self.assertNotEqual(0, len(self.mo.move_raw_ids),
                         'It should be more than 0')