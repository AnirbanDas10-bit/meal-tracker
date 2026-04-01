create table meal_details (
id int auto_increment primary key,
date_ DATETIME default current_timestamp,
meal_type varchar(150) not null,
description_ varchar(200) default NULL
);
create table meal_expense (
id int auto_increment primary key,
detail_id int,
cost decimal(7,2) default NULL check (cost > 0),
 constraint fk_detail_id foreign key (detail_id) references meal_details(id)
);
;
create table excess_spending_alerts (
alert_id int auto_increment primary key,
meal_id int not null,
expense_date datetime not null,
meal_type varchar(150) not null,
actual_cost decimal(7,2) not null check (actual_cost > 0),
excess_amount DECIMAL(7,2) NOT NULL CHECK (excess_amount > 0), 
logged_at DATETIME DEFAULT CURRENT_TIMESTAMP,
constraint fk_meal_id
	foreign key (meal_id)
    references meal_expense(id)
    on delete cascade,
constraint unique_meal_alert 
	unique (meal_id)
);