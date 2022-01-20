-- 1_createdb.sql で作成した db に入る
\c gerosa_linebot

CREATE TABLE player (
  id varchar(100) primary key, 
  full_name varchar(30),
  swing char,
  pitch char,

  created_at timestamp
);

CREATE TABLE game (
  id int primary key, 
  team_name varchar(30),
  game_day int,
  result varchar(3),
  ground varchar(30),

  created_at timestamp
);

CREATE TABLE position (
  position int,
  player_id varchar(100) references player(id),

  primary key (position, player_id),

  created_at timestamp
);

CREATE TABLE pitch (
  player_id varchar(100) references player(id),
  game_id int references game(id),

  primary key (player_id, game_id),
  
  earned_run int,
  inning float,

  created_at timestamp
);

CREATE TABLE bat (
  player_id varchar(100) references player(id),
  game_id int references game(id),
  primary key (player_id, game_id),

  bat int,
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