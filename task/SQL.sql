
-- 表：task_status
INSERT INTO task_status (id, name) VALUES (1, '待认领');
INSERT INTO task_status (id, name) VALUES (2, '进行中');
INSERT INTO task_status (id, name) VALUES (3, '已完成');

-- 表：task_type
INSERT INTO task_type (id, name) VALUES (1, 'Android');
INSERT INTO task_type (id, name) VALUES (2, 'iOS');
INSERT INTO task_type (id, name) VALUES (3, 'H5-医生');
INSERT INTO task_type (id, name) VALUES (4, 'H5-患者');
INSERT INTO task_type (id, name) VALUES (5, '管理后台');
INSERT INTO task_type (id, name) VALUES (6, '诊室');
INSERT INTO task_type (id, name) VALUES (7, '机构');
INSERT INTO task_type (id, name) VALUES (8, '知了官网');
INSERT INTO task_type (id, name) VALUES (9, '间隙期');

-- 表：task_hours
INSERT INTO task_hours (id, month, workDay, dayHours, state) VALUES (1, '202201', 22.0, 7.0, '1');
INSERT INTO task_hours (id, month, workDay, dayHours, state) VALUES (2, '202202', 16.0, 7.0, '1');
INSERT INTO task_hours (id, month, workDay, dayHours, state) VALUES (3, '202203', 23.0, 7.0, '1');


-- 表：task_percent
INSERT INTO task_percent (id, name, percent, ident, score) VALUES (1, '任务延迟折扣', 0.9, 'delay', 0);
INSERT INTO task_percent (id, name, percent, ident, score) VALUES (2, '工作量饱和度阈值', 0.95, 'threshold', 30);
