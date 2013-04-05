ALTER TABLE factories_factory
ADD CONSTRAINT factories_factory_name_check
CHECK (name ~ '^[a-z][a-z0-9_-]*$');
