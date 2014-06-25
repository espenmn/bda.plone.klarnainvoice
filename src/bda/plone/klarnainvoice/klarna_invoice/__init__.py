# -*- coding: utf-8 -*-

import logging
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.uuid.utils import uuidToURL

#from bda.plone.orders.common import get_order
from bda.plone.invoice import (
                               Payment,
                               Payments,
                               )
from bda.plone.invoice.interfaces import IPaymentData
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
        checkout_uri     =  settings.klarna_checkout_uri
        confirmation_uri =  settings.klarna_confirmation_uri
        push_uri         =  settings.klarna_push_uri
        
        #Add the cart items
        cart = list()
        for booking in order_data.bookings:
            cart.append({
                        'quantity': int(booking.attrs['buyable_count']),
                        'reference': uuidToURL(booking.attrs['buyable_uid']),
                        'name': booking.attrs['title'],
                        'unit_price': int((booking.attrs.get('net', 0.0)*100)+(booking.attrs.get('net', 0.0)*booking.attrs.get('vat', 0.0))),
                        'discount_rate': int((booking.attrs['discount_net'])*100),
                        'tax_rate': int(booking.attrs.get('vat', 0.0)*100),
        })
        
        create_data = {}
        create_data["cart"] = {"items": []}
        
        for item in cart:
            create_data["cart"]["items"].append(item)
        
        #Configure the checkout order
        #import pdb; pdb.set_trace()
        create_data['purchase_country'] = 'NO'
        create_data['purchase_currency'] = currency
        create_data['locale'] = 'nb-no'
        
        create_data['shipping_address'] = {
            'email'        : order['personal_data.email'],
            'postal_code'  : order['billing_address.zip'],
        }
        
        create_data['merchant'] = {
            'id'                : eid,
            'terms_uri'         : terms_uri,
            'checkout_uri'      : checkout_uri,
            'confirmation_uri'  : confirmation_uri,
            'push_uri'          : push_uri,
        }
        
        
        # Create a checkout order
        klarnacheckout.Order.base_uri = \
            'https://checkout.testdrive.klarna.com/checkout/orders'
        klarnacheckout.Order.content_type = \
            'application/vnd.klarna.checkout.aggregated-order-v2+json'
        
        connector = klarnacheckout.create_connector(shared_secret)
        
        order = klarnacheckout.Order(connector)
        order.create(create_data)
        
        # Render the checkout snippet
        
        order.fetch()
        
        # Store location of checkout session
        #session["klarna_checkout"] = order.location
        
        # Display checkout
        return "<div>%s</div>" % (order["gui"]["snippet"])


#class KlarnaInvoicePaid(BrowserView):
#    """
#        for klarnas PUSH
#    """
#
#    def __call__(self):
#        self.request.response.setStatus(201)