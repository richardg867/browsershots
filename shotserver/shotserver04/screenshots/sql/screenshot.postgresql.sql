ALTER TABLE screenshots_screenshot
ADD CONSTRAINT screenshots_screenshot_hashkey_check
CHECK (hashkey ~ '^[0-9a-f]{32}$');

ALTER TABLE screenshots_screenshot
ADD CONSTRAINT screenshots_screenshot_width_check
CHECK (640 <= width and width <= 1680);

ALTER TABLE screenshots_screenshot
ADD CONSTRAINT screenshots_screenshot_aspect_ratio_check
CHECK (width / 2 <= height and height <= width * 4);
