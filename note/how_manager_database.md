# MySQL
1. for add column into table
ALTER TABLE tbl_preventions
ADD COLUMN priority INT NOT NULL DEFAULT 1
AFTER image;
# ----------
2.for show propity table all
DESCRIBE tbl_preventions;