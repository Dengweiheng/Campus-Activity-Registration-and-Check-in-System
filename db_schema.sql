-- 创建数据库
CREATE DATABASE IF NOT EXISTS campus_activity_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE campus_activity_system;

-- 用户表 (对应 Django AbstractUser + 扩展字段)
CREATE TABLE `users_user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    `password` VARCHAR(128) NOT NULL COMMENT '密码(哈希)',
    `last_login` DATETIME DEFAULT NULL COMMENT '最后登录时间',
    `is_superuser` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否超级管理员',
    `username` VARCHAR(150) NOT NULL UNIQUE COMMENT '用户名',
    `first_name` VARCHAR(150) NOT NULL DEFAULT '' COMMENT '名',
    `last_name` VARCHAR(150) NOT NULL DEFAULT '' COMMENT '姓',
    `email` VARCHAR(254) NOT NULL DEFAULT '' COMMENT '邮箱',
    `is_staff` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否管理人员',
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
    `date_joined` DATETIME NOT NULL COMMENT '注册时间',
    `real_name` VARCHAR(50) DEFAULT NULL COMMENT '真实姓名',
    `student_id` VARCHAR(20) DEFAULT NULL COMMENT '学号/工号',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    `role` VARCHAR(20) NOT NULL DEFAULT 'student' COMMENT '角色: student/organizer/admin'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';

-- 活动表
CREATE TABLE `activities_activity` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '活动ID',
    `title` VARCHAR(255) NOT NULL COMMENT '活动标题',
    `description` LONGTEXT COMMENT '活动描述',
    `location` VARCHAR(255) NOT NULL COMMENT '活动地点',
    `start_time` DATETIME NOT NULL COMMENT '活动开始时间',
    `end_time` DATETIME NOT NULL COMMENT '活动结束时间',
    `reg_deadline` DATETIME NOT NULL COMMENT '报名截止时间',
    `max_participants` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '最大人数限制 (0 表示不限)',
    `current_participants` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '当前已报名人数',
    `qr_code` VARCHAR(100) DEFAULT NULL COMMENT '签到二维码图片路径',
    `qr_token` CHAR(32) NOT NULL UNIQUE COMMENT '二维码唯一令牌 (UUID, 防伪造)',
    `organizer_id` INT NOT NULL COMMENT '发布者ID',
    `status` VARCHAR(20) NOT NULL DEFAULT 'draft' COMMENT '状态: draft/published/ongoing/finished/cancelled',
    `created_at` DATETIME NOT NULL COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL COMMENT '更新时间',
    FOREIGN KEY (`organizer_id`) REFERENCES `users_user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='校内活动信息表';

-- 报名表
CREATE TABLE `activities_registration` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '报名流水ID',
    `activity_id` BIGINT NOT NULL COMMENT '活动ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `registration_time` DATETIME NOT NULL COMMENT '报名操作时间',
    `status` VARCHAR(20) NOT NULL DEFAULT 'registered' COMMENT '状态: registered/cancelled',
    FOREIGN KEY (`activity_id`) REFERENCES `activities_activity`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users_user`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uniq_user_activity` (`user_id`, `activity_id`) COMMENT '每用户每活动仅一条记录'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='活动报名记录表';

-- 签到表
CREATE TABLE `activities_checkin` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '签到记录ID',
    `registration_id` BIGINT NOT NULL COMMENT '对应报名记录ID',
    `check_in_time` DATETIME NOT NULL COMMENT '签到时间',
    `status` VARCHAR(20) NOT NULL DEFAULT 'normal' COMMENT '状态: normal-正常, late-迟到',
    `ip_address` CHAR(39) DEFAULT NULL COMMENT '签到IP地址 (IPv4/IPv6, 防代签)',
    `device_info` VARCHAR(512) DEFAULT NULL COMMENT '签到设备UA信息 (防代签)',
    FOREIGN KEY (`registration_id`) REFERENCES `activities_registration`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uniq_registration` (`registration_id`) COMMENT '每报名记录只能签到一次'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='活动签到记录表';


-- ============================================================
-- 测试数据
-- ============================================================

-- 用户测试数据 (密码均为 pbkdf2_sha256 哈希，原始密码: Test@1234)
INSERT INTO `users_user`
    (`password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `real_name`, `student_id`, `phone`, `role`)
VALUES
    -- 管理员
    ('pbkdf2_sha256$720000$testadmin$hashedpassword001==', '2026-03-18 09:00:00', TRUE,  'admin',      '', '', 'admin@campus.edu.cn',      TRUE,  TRUE, '2025-09-01 08:00:00', '系统管理员', 'A000001', '13800000001', 'admin'),
    -- 活动组织者
    ('pbkdf2_sha256$720000$testorg1$hashedpassword002==',  '2026-03-17 10:30:00', FALSE, 'org_zhang',  '', '', 'zhang@campus.edu.cn',      FALSE, TRUE, '2025-09-02 08:30:00', '张志远',   'T202001',  '13800000002', 'organizer'),
    ('pbkdf2_sha256$720000$testorg2$hashedpassword003==',  '2026-03-15 14:00:00', FALSE, 'org_liu',    '', '', 'liu@campus.edu.cn',        FALSE, TRUE, '2025-09-03 09:00:00', '刘晓敏',   'T202002',  '13800000003', 'organizer'),
    -- 普通学生
    ('pbkdf2_sha256$720000$testu1$hashedpassword004==',    '2026-03-19 08:00:00', FALSE, 'stu_wang',   '', '', 'wang@stu.campus.edu.cn',   FALSE, TRUE, '2025-09-05 10:00:00', '王小明',   'S20230101', '13900000001', 'student'),
    ('pbkdf2_sha256$720000$testu2$hashedpassword005==',    '2026-03-18 17:00:00', FALSE, 'stu_li',     '', '', 'li@stu.campus.edu.cn',     FALSE, TRUE, '2025-09-06 10:30:00', '李梦琪',   'S20230102', '13900000002', 'student');


-- 活动测试数据
INSERT INTO `activities_activity`
    (`title`, `description`, `location`, `start_time`, `end_time`, `reg_deadline`, `max_participants`, `current_participants`, `qr_code`, `qr_token`, `organizer_id`, `status`, `created_at`, `updated_at`)
VALUES
    (
        '2026年春季校园马拉松',
        '全校师生健康跑活动，5公里组、10公里组自由选择，完赛即得纪念品。',
        '学校田径场及校园环线',
        '2026-04-05 07:30:00', '2026-04-05 12:00:00', '2026-04-03 23:59:00',
        500, 3, NULL, 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4',
        2, 'published', '2026-03-01 10:00:00', '2026-03-10 10:00:00'
    ),
    (
        'Python & AI 技术分享沙龙',
        '邀请业界嘉宾分享大模型应用开发实战经验，内含 Demo 演示和互动 Q&A 环节。',
        '图书馆报告厅（3楼）',
        '2026-03-28 14:00:00', '2026-03-28 17:30:00', '2026-03-27 18:00:00',
        120, 2, NULL, 'b2c3d4e5f6a7b2c3d4e5f6a7b2c3d4e5',
        2, 'published', '2026-03-10 09:00:00', '2026-03-12 11:00:00'
    ),
    (
        '校园摄影大赛作品展',
        '展出本届摄影大赛获奖及优秀入围作品，欢迎全校同学前来观展投票。',
        '艺术楼一楼展厅',
        '2026-03-20 09:00:00', '2026-03-25 18:00:00', '2026-03-19 23:59:00',
        0, 2, NULL, 'c3d4e5f6a7b8c3d4e5f6a7b8c3d4e5f6',
        3, 'ongoing', '2026-03-08 14:00:00', '2026-03-19 08:00:00'
    ),
    (
        '职业规划与简历指导讲座',
        '就业指导中心联合知名企业HR，为大四及研究生提供简历诊断和面试技巧培训。',
        '综合楼 201 报告厅',
        '2026-03-15 15:00:00', '2026-03-15 17:00:00', '2026-03-14 20:00:00',
        80, 2, NULL, 'd4e5f6a7b8c9d4e5f6a7b8c9d4e5f6a7',
        3, 'finished', '2026-03-05 16:00:00', '2026-03-15 17:10:00'
    ),
    (
        '新生迎新晚会彩排',
        '2026级新生迎新晚会节目彩排，参演同学请准时到场，携带演出服装。',
        '大学生活动中心主舞台',
        '2026-04-10 18:30:00', '2026-04-10 21:30:00', '2026-04-08 23:59:00',
        200, 1, NULL, 'e5f6a7b8c9d0e5f6a7b8c9d0e5f6a7b8',
        2, 'draft', '2026-03-18 20:00:00', '2026-03-18 20:00:00'
    );


-- 报名测试数据 (每表5条)
INSERT INTO `activities_registration`
    (`activity_id`, `user_id`, `registration_time`, `status`)
VALUES
    -- 王小明 报名 活动1（春季马拉松）
    (1, 4, '2026-03-11 10:15:00', 'registered'),
    -- 李梦琪 报名 活动1（春季马拉松）
    (1, 5, '2026-03-11 11:30:00', 'registered'),
    -- 王小明 报名 活动2（Python沙龙）
    (2, 4, '2026-03-12 09:00:00', 'registered'),
    -- 李梦琪 报名 活动3（摄影展）
    (3, 5, '2026-03-13 14:20:00', 'registered'),
    -- 李梦琪 报名 活动4（职业规划讲座）
    (4, 5, '2026-03-08 09:30:00', 'registered');

-- 注意：以下额外记录超出5条基础要求，仅供参考，可按需追加
-- (4, 4, '2026-03-08 08:00:00', 'cancelled'),  -- 王小明取消报名活动4
-- (3, 1, '2026-03-14 08:00:00', 'registered'), -- 管理员报名活动3


-- 签到测试数据 (5条，对应已报名且活动已进行的记录)
-- registration id 对应顺序: 1=王小明/马拉松, 2=李梦琪/马拉松, 3=王小明/Python沙龙, 4=李梦琪/摄影展, 5=李梦琪/职业规划
INSERT INTO `activities_checkin`
    (`registration_id`, `check_in_time`, `status`, `ip_address`, `device_info`)
VALUES
    -- 李梦琪 签到 活动3（摄影展，正常）
    (4, '2026-03-20 09:05:00', 'normal', '192.168.1.101',
     'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'),
    -- 李梦琪 签到 活动4（职业规划讲座，正常）
    (5, '2026-03-15 15:02:00', 'normal', '192.168.1.102',
     'Mozilla/5.0 (Android 14; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Mobile Safari/537.36'),
    -- 王小明 签到 活动2（Python沙龙，迟到）
    (3, '2026-03-28 14:35:00', 'late',   '192.168.1.103',
     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36'),
    -- 王小明 签到 活动1（春季马拉松，正常）
    (1, '2026-04-05 07:32:00', 'normal', '10.0.0.55',
     'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'),
    -- 李梦琪 签到 活动1（春季马拉松，迟到）
    (2, '2026-04-05 08:10:00', 'late',   '10.0.0.56',
     'Mozilla/5.0 (Android 13; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Mobile Safari/537.36'); 