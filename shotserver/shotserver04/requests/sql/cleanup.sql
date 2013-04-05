DELETE FROM "requests_requestgroup" WHERE NOT EXISTS (
SELECT * FROM "requests_request"
WHERE "requests_request"."request_group_id" = "requests_requestgroup"."id");
