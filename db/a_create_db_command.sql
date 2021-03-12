/* 
 【basic.db3】
*/
/* create 表單 */
CREATE TABLE "basic" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"equity"	NUMERIC,
	"location"	TEXT,
	"assetValue"	NUMERIC,
	"business"	TEXT,
	"businessRate"	TEXT,
	PRIMARY KEY("id","name")
);

/* create 表單 */
CREATE TABLE "news" (
	"id"	INTEGER NOT NULL,
	"updateTime"	TEXT DEFAULT '',
	"newsList"	BLOB,
	PRIMARY KEY("id")
);
