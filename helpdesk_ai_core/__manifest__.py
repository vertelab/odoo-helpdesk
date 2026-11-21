# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk: AI Coworker',
    'version': '18.0.1.0.0',
    'summary': 'AI coworker for helpdesk — ticket context, tools and skills.',
    'description': '''
Helpdesk AI Coworker
====================

    Built on ai_agent_core, the same pattern as project_ai.

    Features:

        - Session context: `ticket_id` on ai.coworker.session, so cost
          context, lineage and memory attach to the ticket.
        - Resolver `helpdesk_partner`: derives the customer from the ticket.
        - Tools: ticket_get, ticket_set_stage, ticket_update_fields,
          ticket_add_message.
        - Coworker "Helpdesk" (supervisor) with its own skills.

    WHY A SEPARATE MODULE: the existing `helpdesk_ai` is built on the old
    `ai_agent` stack (ai.memory, ai.quest.session, ai.quest). ai_agent_core
    is incompatible with ai_agent — they define the same models — so that
    module cannot be extended with ai.coworker.session. This module is the
    ai_agent_core-native replacement.

    MODEL CHOICE: OCA `helpdesk_mgmt`, not Odoo Enterprise `helpdesk`.
    ''',
    'category': 'Helpdesk',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'depends': [
        'helpdesk_mgmt',
        'ai_agent_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/helpdesk_tools.xml',
        'data/helpdesk_skills.xml',
        'data/helpdesk_coworkers.xml',
        'data/helpdesk_agents.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
