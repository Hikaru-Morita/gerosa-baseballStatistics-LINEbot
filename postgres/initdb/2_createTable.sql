-- 1_createdb.sql で作成した db に入る
\c gerosa_linebot

CREATE TABLE player (
  id varchar(100) primary key, 
  full_name varchar(30) NOT NULL,
  uniform_number int,
  swing varchar(3),
  pitch varchar(3),

  created_at timestamp
);

CREATE TABLE game (
  id int primary key, 
  team_name varchar(30) NOT NULL,
  game_day int NOT NULL,
  result varchar(3) NOT NULL,
  our_score int,
  against_score int, 
  ground varchar(30) NOT NULL,
  meridian varchar(2),

  created_at timestamp
);

CREATE TABLE position (
  position int NOT NULL,
  player_id varchar(100) references player(id) NOT NULL,

  primary key (position, player_id),

  created_at timestamp
);

CREATE TABLE pitch (
  player_id varchar(100) references player(id) NOT NULL,
  game_id int references game(id) NOT NULL,

  primary key (player_id, game_id),
  
  earned_run int NOT NULL,
  inning float NOT NULL,

  created_at timestamp
);

CREATE TABLE bat (
  player_id varchar(100) references player(id) NOT NULL,
  game_id int references game(id) NOT NULL,
  primary key (player_id, game_id),

  bat int NOT NULL,
  home_run int,
  base_hit int,
  two_base_hit int,
  three_base_hit int,
  run int,
  sacrifice int,
  four_ball int,
  dead_ball int,

  created_at timestamp
);