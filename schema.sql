create table if not exists subject (
  subject_id integer primary key autoincrement,
  subject_name string not null,
  subject_memo string
);