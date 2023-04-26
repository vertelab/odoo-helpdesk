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
    'name': "Helpdesk: Escalation",
    'version': '14.0',
    'summary': 'Adds Ticket-to-Task Escalation',
    'description': 
        """Enhances the Helpdesk module by introducing an additional action button in the ticket form view, enabling users to seamlessly convert tickets into tasks.""",
    'category': 'Productivity',
    'website': "https://vertel.se/apps/odoo-helpdesk/helpdesk_escalation",
    'repository': 'https://github.com/vertelab/odoo-helpdesk',
    'images': ['/static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'depends': ['helpdesk_mgmt', 'project'],
    'data': [
        'data/server_actions.xml',
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
