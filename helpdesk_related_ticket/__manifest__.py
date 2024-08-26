# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2023 Vertel AB (<robin.calvin@vertel.se>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#
# https://www.odoo.com/documentation/16.0/reference/module.html
#
{
    'name': 'Helpdesk: Related Ticket',
    'version': '0.1',
    'summary': 'Helpdesk Related Ticket',
    'category': 'Helpdesk',
    'description': """
    
    """,
    'license': 'AGPL-3',
    'author': 'Vertel AB',
    'maintainer': 'Vertel AB',
    'contributor': '',
    'website': 'https://vertel.se/apps/odoo-helpdesk/helpdesk_related_ticket',
    'images': ['static/description/banner.png'], # 560x280 px.
    'repository': 'https://github.com/vertelab/odoo-helpdesk',
    # Any module necessary for this one to work correctly
    
    'depends': ['helpdesk_mgmt'],
    'data': [
        'views/helpdesk_ticket_templates.xml',
        'views/helpdesk_ticket_view.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
}
