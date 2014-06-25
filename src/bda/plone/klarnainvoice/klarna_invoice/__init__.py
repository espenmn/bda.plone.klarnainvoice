    # -*- coding: utf-8 -*-

import klarna

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
        eid = settings.klarna_eid
        
        # Shared Secret
        shared_secret = settings.klarna_secret
        
        #other settings from control panel
        terms_uri        =  settings.klarna_terms_uri
        confirmation_uri =  settings.klarna_confirmation_uri
        
        #Initialize the Klarna object
        config = klarna.Config(
            eid=eid,
            secret=shared_secret,
            country='NO',
            language='NO',
            currency=currency,
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
                        qty = int(booking.attrs['buyable_count']),
                        title = booking.attrs['title'],
                        price = int((booking.attrs.get('net', 0.0)*100)+(booking.attrs.get('net', 0.0)*booking.attrs.get('vat', 0.0))),
                        discount = int((booking.attrs['discount_net'])*100),
                        vat = int(booking.attrs.get('vat', 0.0)*100),
                        flags = 'GoodsIs.INC_VAT')
                        
        #Add Consumer Information
        addr = klarna.Address(
            email= order['personal_data.email'],
            telno='',
            cellno='015 2211 3356',
            fname='Testperson-de',
            lname='Approved',
            careof='',
            street='Hellersbergstraße',
            zip=billing_address.zip,
            city='Oslo',
            country='NO')
            
        k.shipping = addr
        k.billing = addr
        
        ## Set customer IP
        k.clientip = '78.47.10.94'
        
        (reservation_number, order_status) = k.reserve_amount(
            data['amount'],
            Gender.MALE,
            pclass=klarna.PClass.Type.INVOICE
        )
        