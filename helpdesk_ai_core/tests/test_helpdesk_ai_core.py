# -*- coding: utf-8 -*-
"""Tester för helpdesk_ai_core — kontext, resolver och verktyg."""

from odoo.tests.common import TransactionCase


class TestHelpdeskContext(TransactionCase):
    """Sessionens domänkontext."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Testkund AB'})
        cls.team = cls.env['helpdesk.ticket.team'].create({
            'name': 'Testteam',
        })
        cls.ticket = cls.env['helpdesk.ticket'].create({
            'name': 'Testärende',
            'description': 'Testbeskrivning',
            'partner_id': cls.partner.id,
            'team_id': cls.team.id,
        })

    def _new_session(self):
        return self.env['ai.coworker.session'].create({
            'init_type': 'web_ui',
        })

    def test_capture_context_sets_ticket_and_partner(self):
        """_capture_context sätter ticket_id och härleder partner."""
        session = self._new_session()
        session._capture_context(ticket=self.ticket)
        self.assertEqual(session.ticket_id, self.ticket)
        self.assertEqual(session.partner_id, self.partner)

    def test_capture_context_keeps_existing_partner(self):
        """En satt partner skrivs inte över av ärendets kund."""
        other = self.env['res.partner'].create({'name': 'Annan kund'})
        session = self._new_session()
        session.partner_id = other
        session._capture_context(ticket=self.ticket)
        self.assertEqual(session.ticket_id, self.ticket)
        self.assertEqual(session.partner_id, other,
                         'en satt partner ska behållas')

    def test_resolver_sets_partner_from_ticket(self):
        """helpdesk_partner-resolvern härleder kund ur ärendet."""
        from odoo.addons.helpdesk_ai_core.models.ai_coworker_session import (
            _helpdesk_partner_strategy)
        session = self._new_session()
        session.ticket_id = self.ticket
        session.partner_id = False
        _helpdesk_partner_strategy(session)
        self.assertEqual(session.partner_id, self.partner)

    def test_resolver_does_not_guess(self):
        """Utan ärende sätts ingen partner."""
        from odoo.addons.helpdesk_ai_core.models.ai_coworker_session import (
            _helpdesk_partner_strategy)
        session = self._new_session()
        session.partner_id = False
        _helpdesk_partner_strategy(session)
        self.assertFalse(session.partner_id)

    def test_auto_capture_from_ticket_id(self):
        """'ärende <id>' i prompten fångas till ärende."""
        session = self._new_session()
        session._session_auto_capture(
            'Titta på ärende %s tack' % self.ticket.id)
        self.assertEqual(session.ticket_id, self.ticket)

    def test_auto_capture_does_not_overwrite(self):
        """Senast arbetad kontext vinner — ett satt ärende skrivs inte över."""
        other = self.env['helpdesk.ticket'].create({
            'name': 'Annat ärende',
            'description': 'Annat',
            'partner_id': self.partner.id,
        })
        session = self._new_session()
        session.ticket_id = other
        session._session_auto_capture(
            'Titta på ärende %s' % self.ticket.id)
        self.assertEqual(session.ticket_id, other)


class TestHelpdeskTools(TransactionCase):
    """Verktygens affärslogik (helpdesk.ai)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Verktygskund'})
        cls.stage = cls.env['helpdesk.ticket.stage'].create({
            'name': 'Solved',
        })
        cls.ticket = cls.env['helpdesk.ticket'].create({
            'name': 'Verktygsärende',
            'description': 'Verktygsbeskrivning',
            'partner_id': cls.partner.id,
        })

    def test_ticket_get_returns_fields(self):
        """ticket_get returnerar nummer, kund och etapp."""
        res = self.env['helpdesk.ai'].ticket_get(self.ticket.id)
        self.assertEqual(res['id'], self.ticket.id)
        self.assertEqual(res['partner_name'], 'Verktygskund')
        self.assertIn('number', res)

    def test_ticket_get_missing_ticket(self):
        """Saknat ärende ger ett tydligt fel, inte en krasch."""
        res = self.env['helpdesk.ai'].ticket_get(999999)
        self.assertIn('error', res)

    def test_ticket_set_stage(self):
        """ticket_set_stage flyttar ärendet till en etapp."""
        ok, msg = self.env['helpdesk.ai'].ticket_set_stage(
            self.ticket.id, 'Solved')
        self.assertTrue(ok, msg)
        self.assertEqual(self.ticket.stage_id, self.stage)

    def test_ticket_set_stage_unknown(self):
        """Okänd etapp ger ett åtgärdbart fel."""
        ok, msg = self.env['helpdesk.ai'].ticket_set_stage(
            self.ticket.id, 'Finns Inte')
        self.assertFalse(ok)
        self.assertIn('No stage named', msg)

    def test_ticket_update_fields(self):
        """ticket_update_fields ändrar prioritet."""
        ok, msg = self.env['helpdesk.ai'].ticket_update_fields(
            self.ticket.id, priority='3')
        self.assertTrue(ok, msg)
        self.assertEqual(self.ticket.priority, '3')

    def test_ticket_update_fields_nothing(self):
        """Inga fält angivna ger ett tydligt fel."""
        ok, msg = self.env['helpdesk.ai'].ticket_update_fields(
            self.ticket.id)
        self.assertFalse(ok)
        self.assertIn('Nothing to update', msg)

    def test_ticket_add_message(self):
        """ticket_add_message postar i chatter."""
        before = len(self.ticket.message_ids)
        ok, msg = self.env['helpdesk.ai'].ticket_add_message(
            self.ticket.id, 'Testmeddelande')
        self.assertTrue(ok, msg)
        self.assertGreater(len(self.ticket.message_ids), before)

    def test_ticket_add_message_empty(self):
        """Tomt meddelande vägras."""
        ok, msg = self.env['helpdesk.ai'].ticket_add_message(
            self.ticket.id, '')
        self.assertFalse(ok)
        self.assertIn('Missing message body', msg)
