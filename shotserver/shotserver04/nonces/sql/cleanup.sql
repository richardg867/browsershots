DELETE FROM auth_nonce WHERE created < NOW() - '1:00'::interval;
