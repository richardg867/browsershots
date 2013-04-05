\echo 'Deleting expired nonces...'
DELETE FROM nonces_nonce
WHERE created < NOW() - '3d'::interval;

\echo 'Deleting old factory errors...'
DELETE FROM messages_factoryerror
WHERE occurred < NOW() - '24:00'::interval;

\echo 'Deleting old problem reports...'
DELETE FROM screenshots_problemreport
WHERE reported < NOW() - '30d'::interval;

\echo 'Removing screenshots from old requests...'
UPDATE requests_request
SET screenshot_id = NULL
WHERE screenshot_id IS NOT NULL
AND EXISTS (SELECT 1 FROM requests_requestgroup
    WHERE id = requests_request.request_group_id
    AND user_id IS NULL
    AND submitted < NOW() - '24:00'::interval);
UPDATE requests_request
SET screenshot_id = NULL
WHERE screenshot_id IS NOT NULL
AND EXISTS (SELECT 1 FROM requests_requestgroup
    WHERE id = requests_request.request_group_id
    AND submitted < NOW() - '30d'::interval);

\echo 'Deleting old screenshots...'
DELETE FROM screenshots_screenshot
WHERE uploaded < NOW() - '24:00'::interval
AND user_id IS NULL
AND NOT EXISTS (SELECT 1 FROM requests_request
    WHERE screenshot_id = screenshots_screenshot.id)
AND NOT EXISTS (SELECT 1 FROM screenshots_problemreport
    WHERE screenshot_id = screenshots_screenshot.id);
DELETE FROM screenshots_screenshot
WHERE uploaded < NOW() - '30d'::interval
AND NOT EXISTS (SELECT 1 FROM requests_request
    WHERE screenshot_id = screenshots_screenshot.id)
AND NOT EXISTS (SELECT 1 FROM screenshots_problemreport
    WHERE screenshot_id = screenshots_screenshot.id);

\echo 'Deleting old requests without screenshots...'
DELETE FROM requests_request
WHERE screenshot_id IS NULL
AND EXISTS (SELECT 1 FROM requests_requestgroup
    WHERE id = requests_request.request_group_id
    AND submitted < NOW() - '24:00'::interval)
AND NOT EXISTS (SELECT 1 FROM messages_factoryerror
    WHERE request_id = requests_request.id);

\echo 'Deleting old request groups without requests...'
DELETE FROM requests_requestgroup
WHERE submitted < NOW() - '24:00'::interval
AND NOT EXISTS (SELECT 1 FROM requests_request
    WHERE request_group_id = requests_requestgroup.id);

\echo 'Deleting old websites without request groups...'
DELETE FROM websites_website
WHERE submitted < NOW() - '7d'::interval
AND NOT EXISTS (SELECT 1 FROM requests_requestgroup
    WHERE website_id = websites_website.id)
AND NOT EXISTS (SELECT 1 FROM screenshots_screenshot
    WHERE website_id = websites_website.id);

\echo 'Deleting old domains without websites...'
DELETE FROM websites_domain
WHERE submitted < NOW() - '7d'::interval
AND NOT EXISTS (SELECT 1 FROM websites_website
    WHERE domain_id = websites_domain.id)
AND NOT EXISTS (SELECT 1 FROM priority_domainpriority
    WHERE domain_id = websites_domain.id);

\echo 'Deleting old browsers without requests or screenshots...'
DELETE FROM browsers_browser
WHERE created < NOW () - '30d'::interval
AND (last_upload < NOW() - '30d'::interval OR last_upload IS NULL)
AND NOT EXISTS (SELECT 1 FROM screenshots_screenshot
    WHERE browser_id = browsers_browser.id)
AND NOT EXISTS (SELECT 1 FROM requests_request
    WHERE browser_id = browsers_browser.id);

\echo 'Deleting color depths from unused factories...'
DELETE FROM factories_colordepth
WHERE EXISTS (SELECT 1 FROM factories_factory
    WHERE factories_factory.id = factory_id
    AND created < NOW() - '30d'::interval
    AND last_upload IS NULL);

\echo 'Deleting screen sizes from unused factories...'
DELETE FROM factories_screensize
WHERE EXISTS (SELECT 1 FROM factories_factory
    WHERE factories_factory.id = factory_id
    AND created < NOW() - '30d'::interval
    AND last_upload IS NULL);

\echo 'Deleting old factories without browsers or screenshots...'
DELETE FROM factories_factory
WHERE created < NOW () - '30d'::interval
AND last_upload IS NULL
AND NOT EXISTS (SELECT 1 FROM browsers_browser
    WHERE factory_id = factories_factory.id)
AND NOT EXISTS (SELECT 1 FROM requests_request
    WHERE factory_id = factories_factory.id)
AND NOT EXISTS (SELECT 1 FROM screenshots_screenshot
    WHERE factory_id = factories_factory.id)
AND NOT EXISTS (SELECT 1 FROM factories_screenshotcount
    WHERE factory_id = factories_factory.id)
AND NOT EXISTS (SELECT 1 FROM factories_colordepth
    WHERE factory_id = factories_factory.id)
AND NOT EXISTS (SELECT 1 FROM factories_screensize
    WHERE factory_id = factories_factory.id);
