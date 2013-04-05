ALTER TABLE messages_factoryerror
DROP CONSTRAINT messages_factoryerror_factory_id_fkey;
ALTER TABLE messages_factoryerror
ADD CONSTRAINT messages_factoryerror_factory_id_fkey
FOREIGN KEY (factory_id) REFERENCES factories_factory(id)
ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
