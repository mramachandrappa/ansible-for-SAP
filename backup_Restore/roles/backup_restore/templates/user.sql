create user bkp_operator password Initial1;
grant backup operator to bkp_operator;
alter user bkp_operator disable password lifetime;