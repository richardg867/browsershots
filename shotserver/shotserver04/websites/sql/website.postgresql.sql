ALTER TABLE websites_website
ADD CONSTRAINT websites_website_url_check
CHECK (url ~* E'^https?://(|[\\w:]+@)(([a-z0-9_-]+\\.)+[a-z]+|(\\d{1,3}\\.){3}\\d{1,3}|(0x[0-9a-f]{2}\\.){3}0x[0-9a-f]{2}|\\d+)(:\\d+)?/\\S*$');
