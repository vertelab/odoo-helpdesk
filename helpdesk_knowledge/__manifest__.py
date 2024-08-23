# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2023- Vertel AB (<https://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Helpdesk: Knowledge",
    'version': '0.1',
    'summary': 'Adds link to Knowledge and forum.',
    'description': """
    Adds link to Knowledge and forum.
    """,
    'category': 'Productivity',
    'license': 'AGPL-3',
    'website': "https://vertel.se/apps/odoo-helpdesk/helpdesk_knowledge",
    'repository': 'https://github.com/vertelab/odoo-helpdesk',
    'images': ['/static/description/banner.png'], # 560x280 px.
    'repository': 'https://github.com/vertelab/odoo-helpdesk',
    # Any module necessary for this one to work correctly
    
    'depends': ['helpdesk_mgmt', 'document_knowledge','website_forum'],
    'data': [
        'data/server_actions.xml',
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
