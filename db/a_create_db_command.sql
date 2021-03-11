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

/*
 【news.db3】
*/
/* create 表單 */
CREATE TABLE "news" (
	"id"	INTEGER,
	"stockID"	INTEGER NOT NULL,
	"date"	TEXT,
	"dateStr"	TEXT,
	"title"	TEXT,
	"url"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
/* 個股取新聞時做使用 */
CREATE INDEX "stockID_index" ON "news" (
	"stockID"
);
/* 做新增新聞時使用 */
CREATE INDEX "news_add_index" ON "news" (
	"date", "title"
)
