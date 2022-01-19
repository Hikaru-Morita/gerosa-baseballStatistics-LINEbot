CREATE TABLE player (
  id integer, 
  full_name varchar(30),
  swing char,
  pitch char,

  created_at timestamp
);

CREATE TABLE game (
  id integer, 
  team_name varchar(30),
  game_day int,
  result varchar(3),
  ground varchar(30),

  created_at timestamp
);

CREATE TABLE position (
  id int,
  position int,
  player_id int,

  created_at timestamp
);

CREATE TABLE pitch (
  id int,
  player_id int,
  game_id int,
  
  earned_run int,
  inning float,

  created_at timestamp
);

CREATE TABLE bat (
  id int,
  player_id int,
  game_id int,

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