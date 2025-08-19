-- SPDX-FileCopyrightText: 2023 Coop IT Easy SC
--
-- SPDX-License-Identifier: AGPL-3.0-or-later

UPDATE ir_cron SET active='f';
-- not sure if all the other fields need to be updated when the server is set inactive
UPDATE ir_mail_server SET active='f', smtp_encryption='none', smtp_port=1025, smtp_host='localhost',smtp_user='', smtp_pass='';
UPDATE fetchmail_server SET active='f', password='', server='localhost';
