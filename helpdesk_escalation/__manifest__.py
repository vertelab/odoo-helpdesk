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
    'version': '16.0',
    'summary': 'Adds Ticket-to-Task Escalation',
    'description': 
        """
        * Overview
        
            Enhances the Helpdesk module by introducing an additional action button in the ticket form view, enabling users to seamlessly convert tickets into tasks.
        
        * Features
        
            - Introduction of New Escalation Feature

                The feature introduces an enhancement to the action menu within the Helpdesk ticket view form, by adding an option for ticket 
                escalation to a task. This functionality will extract all relevant information, such as attachments and messages, from the 
                selected ticket to generate a new task. However, it's important to note that this will not work if there is an existing task
                associated with the ticket or if a 'Project' hasn't been designated.

            - Archiving and Redirection Post Task Creation

                Upon successful creation of the task, the originating ticket is archived to maintain an efficient workflow. Users will be 
                automatically redirected to the freshly created task for immediate attention.

            - Traceability with Automatic Message Creation

                For transparency and reference, an automatic message will be added to the task. This message will indicate that the task was
                created based on a specific Helpdesk ticket and will also include a link back to the original ticket. Similarly, a 
                corresponding message will be created on the archived Helpdesk ticket, indicating its utilization in the creation of a task
                and providing a link to this task. These provisions ensure a seamless transition and comprehensive traceability between the
                ticket and its subsequent task.
            
            """,
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
