-- To be run from root of repo
-- sqlite3 db/twokinds_patreon.db  < scripts/create_schema.sql
drop table patreon;
drop table tags;

CREATE TABLE IF NOT EXISTS "patreon"(
    "vault_id" INTEGER primary key,
    "id" INTEGER,
    "title" TEXT,
    "description" TEXT,
    "filename" TEXT,
    "type"  TEXT,
    "url" TEXT,
    "date" TEXT
);

CREATE TABLE IF NOT EXISTS "tags"(
    "id" INTEGER,
    "tag" TEXT
);

