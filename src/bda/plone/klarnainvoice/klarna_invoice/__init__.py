    # -*- coding: utf-8 -*-

import sys
import klarna

from klarna.const import *

import logging
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.uuid.utils import uuidToURL

#from bda.plone.orders.common import get_order
from bda.plone.payment import (
                               Payment,
                               Payments,
                               )
from bda.plone.payment.interfaces import IPaymentData
from bda.plone.orders.common import OrderData
from bda.plone.shop.interfaces import IShopSettings

from bda.plone.klarnainvoice import IKlarnaInvoiceSettings




_ = MessageFactory('bda.plone.klarnainvoice')
logger = logging.getLogger('bda.plone.invoice')



class KlarnaInvoice(Payment):
    pid = 'klarna'
    label = _('klarnainvoice', 'Klarna Invoice')
    
    def init_url(self, uid):
        return '%s/@@klarna_invoice?uid=%s' % (self.context.absolute_url(), uid)


class KlarnaInvoicePay(BrowserView):
    """
        uses klarna  
        """
    
    def __call__(self, **kw):
        uid = self.request['uid']
        base_url = self.context.absolute_url()
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IKlarnaInvoiceSettings)
        
        data = IPaymentData(self.context).data(uid)
        
        #amount = data['amount']
        #description = data['description']
        #ordernumber = data['ordernumber']
        currency = data['currency']

        #get items for klarna
        order_data = OrderData(self.context, uid)
        order = dict(order_data.order.attrs)
        
        # Merchant ID
        eid = 2280
        
        # Shared Secret
        shared_secret = 'qzjaNjloMvifB6z'
        
        
        #Initialize the Klarna object
        config = klarna.Config(
            eid=str(eid),
            secret=str(shared_secret),
            country='NO',
            language='NB',
            currency='NOK',
            mode='beta',
            pcstorage='json',
            pcuri='/srv/pclasses.json',
            scheme='https',
            candice=True,
        )

        k = klarna.Klarna(config)
        k.init()
        
        
        #Add the cart items
        for booking in order_data.bookings:
            k.add_article(
                        qty = 1,
                        title = 'tittel',
                        price =  100,
                        vat =  25,
                        flags = GoodsIs.INC_VAT)
                        
        import pdb; pdb.set_trace()
        #Add Consumer Information
        addr = klarna.Address(
            email= 'youremail@email.com',
            telno='',
            cellno='40 123 456',
            fname='Testperson-no',
            lname='Approved',
            careof='',
            street='Sæffleberggate 56',
            zip='0563',
            city='Oslo',
            country='NO')
            
        k.shipping = addr
        k.billing = addr
        
        
        ## Set customer IP
        k.clientip = '84.48.92.31'
        
        (reservation_number, order_status) = k.reserve_amount(
            '011215',
            1,
            pclass=klarna.PClass.Type.INVOICE
        )
        