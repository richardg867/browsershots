ALTER TABLE nonces_nonce
ADD CONSTRAINT nonces_nonce_hashkey_check
CHECK (hashkey ~ '^[0-9a-f]{32}$');
