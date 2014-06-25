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
            eid=eid,
            secret=shared_secret,
            country='nor',
            language='no',
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
                        
        #Add Consumer Information
        addr = klarna.Address(
            email= order['personal_data.email'],
            telno='',
            cellno='015 2211 3356',
            fname='Testperson-no',
            lname='Approved',
            careof='',
            street='Hellersbergstraße',
            zip='0563',
            city='Oslo',
            country='NO')
            
        k.shipping = addr
        k.billing = addr
        
        
        ## Set customer IP
        k.clientip = '78.47.10.94'
        
        (reservation_number, order_status) = k.reserve_amount(
            '07071960',
            1,
            pclass=klarna.PClass.Type.INVOICE
        )
        