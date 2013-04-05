TRUNCATE
"screenshots_screenshot",
"requests_request",
"requests_requestgroup",
"websites_website",
"websites_domain";

ALTER SEQUENCE "screenshots_screenshot_id_seq" RESTART WITH 1;
ALTER SEQUENCE "requests_request_id_seq" RESTART WITH 1;
ALTER SEQUENCE "requests_requestgroup_id_seq" RESTART WITH 1;
ALTER SEQUENCE "websites_website_id_seq" RESTART WITH 1;
ALTER SEQUENCE "websites_domain_id_seq" RESTART WITH 1;
