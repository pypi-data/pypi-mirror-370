## 第一步，查询窗口列表，获取窗口id列表（grw_id）
select * gdp_release_window where grw_release_time >= 'start_time' and grw_release_time <= 'end_time';

## 第二步 根据项目名称模糊匹配项目列表
select gp_id from gdp_project where gp_name like '%项目名称%'

## 第三步 根据项目id 匹配迭代id列表
select * gdp_sprint_relation where gsr_target_id in (gp_id列表)

## 第四步 查询迭代表，根据窗口id列表和迭代id列表查询，获取迭代id列表 (gs_id)
select * gdp_sprint where gs_release_win_id in (窗口id列表) and gs_id in (迭代id列表)

## 第五步 获取需求列表信息 如果gt_release_win_id为空则匹配gt_sprint_id字段，不为空匹配gt_release_win_id字段，查询的任务类型id为1,3,4,5,6,7,12
select gt_id,gt_task_no,gt_title from gdp_task 
    where if(gt_release_win_id is null and gt_task_type_id in (1,3,4,5,6,7,12), gt_release_win_id );