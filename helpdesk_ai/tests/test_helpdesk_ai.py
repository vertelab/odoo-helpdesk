# -*- coding: utf-8 -*-
"""Tester för helpdesk_ai — kontext, resolver och verktyg."""

from odoo.tests.common import TransactionCase, tagged


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
        from odoo.addons.helpdesk_ai.models.ai_coworker_session import (
            _helpdesk_partner_strategy)
        session = self._new_session()
        session.ticket_id = self.ticket
        session.partner_id = False
        _helpdesk_partner_strategy(session)
        self.assertEqual(session.partner_id, self.partner)

    def test_resolver_does_not_guess(self):
        """Utan ärende sätts ingen partner."""
        from odoo.addons.helpdesk_ai.models.ai_coworker_session import (
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


# ══════════════════════════════════════════════════════════════════════
# Tillägg (2026-11-21): trådläsning, kundsvar och lat kanal.
# ══════════════════════════════════════════════════════════════════════


@tagged('post_install', '-at_install')
class TestHelpdeskTicketThread(TransactionCase):
    """Läsa tråden och svara kunden."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Ticket = cls.env['helpdesk.ticket']
        cls.Stage = cls.env['helpdesk.ticket.stage']
        cls.Partner = cls.env['res.partner']
        cls.HelpdeskAI = cls.env['helpdesk.ai']

        cls.partner = cls.Partner.create(
            {'name': 'HD Thread Customer', 'is_company': True})
        cls.stage = cls.Stage.create({'name': 'HD Thread New'})
        cls.ticket = cls.Ticket.create({
            'name': 'HD Thread Ticket',
            'description': '<p>Trådtest</p>',
            'partner_id': cls.partner.id,
            'stage_id': cls.stage.id,
        })

    def test_70_ticket_messages_returns_thread(self):
        """ticket_messages returnerar tråden, inte bara beskrivningen.

        Skillnaden mot ticket_get: den ger beskrivningen, den här ger
        samtalet. Behövs innan ett svar föreslås.
        """
        self.ticket.message_post(body='Kunden har svarat igen.')
        res = self.HelpdeskAI.ticket_messages(self.ticket.id)
        self.assertEqual(res['ticket_id'], self.ticket.id)
        self.assertGreater(res['count'], 0)
        bodies = ' '.join(m['body'] for m in res['messages'])
        self.assertIn('svarat igen', bodies)

    def test_71_ticket_messages_limit(self):
        """limit begränsar antalet meddelanden."""
        for i in range(5):
            self.ticket.message_post(body='meddelande %d' % i)
        res = self.HelpdeskAI.ticket_messages(self.ticket.id, limit=2)
        self.assertLessEqual(res['count'], 2)

    def test_72_ticket_messages_missing(self):
        """Okänt id ger error-nyckel."""
        res = self.HelpdeskAI.ticket_messages(999999)
        self.assertIn('error', res)

    def test_73_post_answer_notifies_customer(self):
        """ticket_post_answer sätter subtype mt_comment (når kunden).

        ticket_add_message postar också som 'comment' men utan subtype —
        det blir en intern notering. Skillnaden är hela poängen med det
        här verktyget.
        """
        ok, msg = self.HelpdeskAI.ticket_post_answer(
            self.ticket.id, '<p>Vi har åtgärdat det.</p>')
        self.assertTrue(ok, msg)
        comments = self.ticket.message_ids.filtered(
            lambda m: m.message_type == 'comment')
        self.assertTrue(comments, 'inget kommentarsmeddelande skapades')
        self.assertIn('mt_comment', comments[0].subtype_id.get_external_id()
                      .get(comments[0].subtype_id.id, ''),
                      'subtype mt_comment saknas — kunden notifieras inte')

    def test_74_post_answer_empty(self):
        """Tomt svar postar inget."""
        before = len(self.ticket.message_ids)
        ok, msg = self.HelpdeskAI.ticket_post_answer(self.ticket.id, '  ')
        self.assertFalse(ok)
        self.assertEqual(len(self.ticket.message_ids), before)


@tagged('post_install', '-at_install')
class TestHelpdeskChannel(TransactionCase):
    """Kanalen skapas lat och bär ärendets kontext."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Ticket = cls.env['helpdesk.ticket']
        cls.Stage = cls.env['helpdesk.ticket.stage']
        cls.Partner = cls.env['res.partner']

        cls.partner = cls.Partner.create(
            {'name': 'HD Chan Customer', 'is_company': True})
        cls.stage_open = cls.Stage.create({'name': 'HD Chan New'})
        cls.stage_closed = cls.Stage.create(
            {'name': 'HD Chan Closed', 'closed': True})

    def _ticket(self, **kw):
        vals = {
            'name': 'HD Chan Ticket',
            'description': '<p>x</p>',
            'partner_id': self.partner.id,
            'stage_id': self.stage_open.id,
        }
        vals.update(kw)
        return self.Ticket.create(vals)

    def test_80_no_channel_on_create(self):
        """create() ska INTE skapa någon kanal — den ska vara lat."""
        ticket = self._ticket()
        self.assertFalse(ticket.ai_channel_id,
                         'kanal skapades i create() — ska vara lat')

    def test_81_ensure_creates_channel(self):
        """_ensure_ai_channel() skapar kanalen med ärendenumret."""
        ticket = self._ticket()
        channel = ticket._ensure_ai_channel()
        self.assertTrue(channel)
        self.assertEqual(ticket.ai_channel_id, channel)
        self.assertIn(ticket.number or str(ticket.id), channel.name)

    def test_82_ensure_is_idempotent(self):
        """Två anrop ger samma kanal."""
        ticket = self._ticket()
        self.assertEqual(ticket._ensure_ai_channel(),
                         ticket._ensure_ai_channel())

    def test_83_channel_has_coworker(self):
        """Kanalen ska ha coworkern kopplad (för @mention-routing)."""
        ticket = self._ticket()
        channel = ticket._ensure_ai_channel()
        cw = self.env['ai.coworker'].search(
            [('name', '=', 'Helpdesk')], limit=1)
        self.assertIn(cw, channel.ai_coworker_ids)

    def test_84_channel_carries_ticket_context(self):
        """Kanalen bär ärendets kontext — coworkern vet vad frågan gäller."""
        ticket = self._ticket()
        channel = ticket._ensure_ai_channel()
        channel._capture_ai_context(extra_context={
            'context_model': 'helpdesk.ticket',
            'context_res_id': ticket.id,
            'view_type': 'form',
        })
        recs, view_type = channel._get_ai_context_record()
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs.id, ticket.id)
        self.assertEqual(view_type, 'form')

    def test_85_detect_record_finds_ticket(self):
        """ai.coworker._detect_record() hittar ärendet via kanalen."""
        ticket = self._ticket()
        channel = ticket._ensure_ai_channel()
        channel._capture_ai_context(extra_context={
            'context_model': 'helpdesk.ticket',
            'context_res_id': ticket.id,
            'view_type': 'form',
        })
        cw = self.env['ai.coworker'].search(
            [('name', '=', 'Helpdesk')], limit=1)
        found = cw._detect_record({'channel': channel})
        self.assertTrue(found, '_detect_record hittade inget')
        self.assertEqual(found._name, 'helpdesk.ticket')
        self.assertEqual(found.id, ticket.id)

    def test_86_closing_ticket_closes_channel(self):
        """Stängning av ärendet stänger AI-kanalen."""
        ticket = self._ticket()
        channel = ticket._ensure_ai_channel()
        self.assertTrue(channel.active)
        ticket.write({'stage_id': self.stage_closed.id})
        self.assertFalse(channel.active,
                         'kanalen ska stängas när ärendet stängs')

    def test_87_reopening_ticket_reopens_channel(self):
        """Återöppning öppnar kanalen igen."""
        ticket = self._ticket()
        channel = ticket._ensure_ai_channel()
        ticket.write({'stage_id': self.stage_closed.id})
        ticket.write({'stage_id': self.stage_open.id})
        self.assertTrue(channel.active,
                        'kanalen ska öppnas när ärendet återöppnas')
