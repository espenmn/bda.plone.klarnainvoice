from bda.plone.shop import message_factory as _

from zope import schema
from plone.supermodel import model
from zope.interface import Interface
from zope.interface import provider

from bda.plone.shop.interfaces import IShopSettingsProvider

#from zope.interface import Attribute


@provider(IShopSettingsProvider)
class IKlarnaInvoiceSettings(model.Schema):
    
    model.fieldset( 'klarna',label=_(u'Klarna', default=u'Klarna'),
        fields=[
        'klarna_eid',
        'klarna_secret',
        'klarna_terms_uri',
        'klarna_confirmation_uri',
        ],
    )
                   
    klarna_eid = schema.ASCIILine(title=_(u'klarn_eid', default=u'Eid'),
                 required=True
    )

    klarna_secret = schema.ASCIILine(title=_(u'klarna_secret', default=u'Shared Secret'),
               required=True
    )
    
    klarna_terms_uri = schema.ASCIILine(title=_(u'klarna_terms_uri', default=u'Klarna Terms URI'),
               required=True
    )
    
    klarna_confirmation_uri = schema.ASCIILine(title=_(u'klarna_confirmation_uri', default=u'Confirmation URI'),
               required=True
    )
    
          