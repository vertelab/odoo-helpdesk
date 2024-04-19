#    Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from datetime import datetime
import random


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    team_sla = fields.Boolean(string="Team SLA", compute="_compute_team_sla")
    sla_expired = fields.Boolean(string="SLA expired")
    sla_deadline = fields.Datetime(string="SLA deadline")

    sla_time_to_assigned = fields.Float(string="Time to user assigned", store=True)
    sla_time_to_ongoing = fields.Float(string="Time to Ongoing", store=True)
    sla_time_to_done = fields.Float(string="Time to Done", store=True)

    knowledge_id = fields.Many2one('document.page', string="Artikel")
    forum_id = fields.Many2one('forum.post', string="Forums Post")

    @api.onchange('user_id')
    def calculate_time_to_assigned(self):
        for record in self:
            if record.user_id:
                create_date = record.create_date
                current_time = datetime.now()
                difference_seconds = (current_time - create_date).total_seconds()
                record.sla_time_to_assigned = difference_seconds / 3600

    @api.onchange('stage_id')
    def calculate_time_to_ongoing_done(self):
        for rec in self:
            if rec.stage_id.sla_stage_type == "ongoing":
                create_date = rec.create_date
                current_time = datetime.now()
                difference_seconds = (current_time - create_date).total_seconds()
                rec.sla_time_to_ongoing = difference_seconds / 3600
                # ~ rec.sla_time_to_done = rec.sla_time_to_done
            elif rec.stage_id.sla_stage_type == "done":
                create_date = rec.create_date
                current_time = datetime.now()
                difference_seconds = (current_time - create_date).total_seconds()
                rec.sla_time_to_done = difference_seconds / 3600
                # ~ rec.sla_time_to_ongoing = rec.sla_time_to_ongoing

    def _compute_team_sla(self):
        for rec in self:
            rec.team_sla = rec.team_id.use_sla

    @api.model
    def create_demo_tickets(self, num=100):
        issues = [
            "Network connectivity problem",
            "Software installation failure",
            "Printer not working",
            "Email delivery issue",
            "Slow system performance",
            "Password reset request",
            "Data backup failure",
            "Website down",
            "Application crash",
            "File permissions issue",
            "Server maintenance required",
            "Database connection error",
            "VPN connection problem",
            "Error accessing shared drive",
            "Software licensing issue",
            "Security breach",
            "System update causing errors",
            "Wireless connection dropout",
            "Hardware malfunction",
            "Server overload",
            "Website layout broken",
            "Error in financial calculations",
            "Mobile app crashes on startup",
            "Email attachment corrupted",
            "DNS resolution problem",
            "User unable to log in",
            "Bluetooth connectivity issue",
            "Browser compatibility problem",
            "Data loss due to power outage",
            "External monitor not detected",
            "Remote desktop connection failure",
            "Database query performance degradation",
            "Web server certificate expired",
            "Out of disk space on server",
            "Backup restore failure",
            "Database table corruption",
            "Application freezing randomly",
            "Wireless interference",
            "Printer paper jam",
            "USB device not recognized",
            "Browser hijacking",
            "API endpoint returning errors",
            "Error in credit card processing",
            "SQL injection vulnerability",
            "Unexpected server reboot",
            "Web browser crashing",
            "Authentication token expiration",
            "Operating system not found",
            "Mouse cursor lagging",
            "Internal server error",
            "Audio output not working",
            "Web form submission failure",
            "JavaScript errors on website",
            "Video conferencing software glitch",
            "Email server blacklist issue",
            "Unauthorized access attempt",
            "Mobile app login screen looping",
            "Outdated software version",
            "Malware infection detected",
            "System clock out of sync",
            "Backup tape corruption",
            "Printer driver compatibility issue",
            "Network firewall misconfiguration",
            "Web server timeout errors",
            "Error in billing system calculations",
            "Hard drive failure",
            "DNS cache poisoning",
            "Error in API documentation",
            "Data corruption in database",
            "SQL syntax error",
            "System overheating",
            "Print job stuck in queue",
            "Application memory leak",
            "Broken hyperlink on website",
            "User account locked out",
            "Application GUI layout broken",
            "Certificate revocation list (CRL) issue",
            "Kernel panic",
            "Cross-site scripting (XSS) vulnerability",
            "Server rack power supply failure",
            "SMTP server configuration error",
            "Application server timeout",
            "Hardware RAID array degradation",
            "Web server log file filling disk space",
            "Email bounce-backs due to spam filter",
            "Software patch causing system instability",
            "Database deadlock",
            "Firewall blocking legitimate traffic",
            "Disk fragmentation slowing performance",
            "SQL database replication lag",
            "Broken image links on website",
            "Error in SSL certificate installation",
            "Remote desktop protocol (RDP) disconnects",
            "Data inconsistency in database",
            "Printer out of toner",
            "File synchronization failure",
            "Web server bandwidth exceeded",
            "Invalid SSL certificate",
            "User interface (UI) responsiveness issue",
            "CAPTCHA not displaying correctly",
            "Data center power outage",
            "Kernel module not loading",
            "Server BIOS update required",
            "SQL stored procedure error",
            "Network switch port flapping",
            "Error in log file rotation configuration",
            "Database index corruption",
            "Software API rate limit reached",
            "File server disk quota exceeded",
            "Mobile app push notifications not working",
            "Operating system security vulnerability",
            "Memory module failure",
            "Web server URL redirection loop",
            "VPN tunnel instability",
            "Email server mail queue filling up",
        ]

        team_id = [1]
        type_id = [1]
        user_id = [1]
        time = [0.0, 5.0]
        priority = [0, 1, 2, 3]
        stages = [1, 2, 4]
        x = 0
        while x < num:
            stage = random.choice(stages)
            x = x + 1
            vals = {'name': random.choice(issues),
                    'team_id': random.choice(team_id),
                    'type_id': random.choice(type_id),
                    'user_id': random.choice(user_id),
                    'stage_id': stage,
                    'priority': str(random.choice(priority)),
                    'sla_time_to_assigned': random.uniform(0, 5),
                    'sla_time_to_ongoing': random.uniform(0, 5) if stage != 1 else 0,
                    'sla_time_to_done': random.uniform(0, 5) if stage == 4 else 0,
                    'description': "Help",
                    }

            self.env['helpdesk.ticket'].create(vals)


class HelpdeskTicketStage(models.Model):
    _inherit = "helpdesk.ticket.stage"

    SECTION_SELECTION = [
        ('other', 'Other'),
        ('ongoing', 'Ongoing'),
        ('done', 'Done'),
    ]

    sla_stage_type = fields.Selection(SECTION_SELECTION, string='sla Stage Type', default='other')
