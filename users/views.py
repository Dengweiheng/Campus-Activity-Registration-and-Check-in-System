# ==============================================================================
# 用户模块视图 (users/views.py)
# 负责：用户注册、登录/注销、个人信息维护、用户管理、签到监控、统计大屏与数据导出
# ==============================================================================

import datetime
import csv
import io

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.http import HttpResponse

from .forms import RegisterForm, ProfileUpdateForm
from .models import User


# ----------------------------------------------------------------------
# 1. 基础身份认证视图（注册、登录、注销）
# ----------------------------------------------------------------------

def register_view(request):
    """
    用户注册视图
    - GET 请求：展示注册表单
    - POST 请求：校验表单数据、创建新用户，并自动完成登录
    """
    # 如果用户已经登录，直接重定向到活动列表首页，避免重复注册
    if request.user.is_authenticated:
        return redirect('activities:list')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 表单校验通过，写入数据库（包含密码哈希加密）
            user = form.save()
            # 自动登录，将用户信息写入当前 Session
            login(request, user)
            messages.success(request, f"注册成功，欢迎 {user.real_name or user.username}！")
            return redirect('activities:list')
    else:
        # GET 请求：实例化空白注册表单
        form = RegisterForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """
    用户登录视图
    - GET 请求：展示登录表单
    - POST 请求：验证账号密码，建立登录会话（Session）
    """
    # 已登录用户直接跳转首页
    if request.user.is_authenticated:
        return redirect('activities:list')
    
    if request.method == 'POST':
        # AuthenticationForm 是 Django 内置的登录验证表单，自动处理密码比对
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # 写入 session
            messages.success(request, f"欢迎回来，{user.real_name or user.username}！")
            # 支持登录后跳回原来想访问的页面（如未登录点击报名被拦截时附带的 next 参数）
            next_url = request.GET.get('next') or '/'
            return redirect(next_url)
        else:
            messages.error(request, "用户名或密码错误，请重试。")
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """
    用户注销视图
    - 清除当前客户端的 Session 数据并重定向到登录页
    """
    logout(request)
    messages.info(request, "您已成功退出登录。")
    return redirect('users:login')


# ----------------------------------------------------------------------
# 2. 个人中心与我的报名
# ----------------------------------------------------------------------

@login_required
def profile_view(request):
    """
    个人信息查看与修改视图
    - @login_required：确保只有登录用户可访问
    """
    if request.method == 'POST':
        # instance=request.user 表示修改当前登录用户自己的记录
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "个人信息已更新！")
            return redirect('users:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})


@login_required
def my_registrations_view(request):
    """
    学生端：查看我报名的所有活动及签到状态
    - select_related('activity')：关联查询优化，减少 SQL 查询次数（避免 N+1 查询问题）
    """
    from activities.models import Registration
    registrations = Registration.objects.filter(
        user=request.user
    ).select_related('activity').order_by('-registration_time')
    
    return render(request, 'users/my_registrations.html', {'registrations': registrations})


def role_required(roles):
    """
    自定义权限装饰器工厂：限制仅指定角色的用户或超级管理员可以访问
    :param roles: 允许的角色列表/元组，如 ('admin', 'organizer')
    """
    return user_passes_test(
        lambda u: u.is_authenticated and (u.role in roles or u.is_superuser),
        login_url='users:login'
    )


# ----------------------------------------------------------------------
# 3. 管理员功能：用户管理与签到监控
# ----------------------------------------------------------------------

@login_required
def user_management(request):
    """
    管理员端：用户管理列表
    - 支持按用户名/姓名/学号模糊搜索
    - 支持快捷切换账号启用/禁用状态 (toggle_active)
    - 支持变更用户角色 (set_role)
    - 支持删除指定用户 (delete)
    """
    # 权限校验：仅管理员与超级管理员可操作
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, "您没有权限访问用户管理。")
        return redirect('activities:list')
    
    action = request.POST.get('action')
    uid = request.POST.get('user_id')
    
    # 处理 POST 操作（状态切换 / 角色修改 / 删除）
    if request.method == 'POST' and uid:
        target = User.objects.filter(pk=uid).first()
        # 目标用户存在且不能操作管理员自己
        if target and target != request.user:
            if action == 'toggle_active':
                # 切换启用/禁用状态
                target.is_active = not target.is_active
                target.save(update_fields=['is_active'])
                messages.success(request, f"用户 {target.username} 已{'启用' if target.is_active else '禁用'}。")
            elif action == 'set_role':
                # 修改角色（学生 / 组织者 / 管理员）
                new_role = request.POST.get('role')
                if new_role in ('student', 'organizer', 'admin'):
                    target.role = new_role
                    target.save(update_fields=['role'])
                    messages.success(request, f"用户 {target.username} 角色已更新为 {new_role}。")
            elif action == 'delete':
                # 删除用户
                target.delete()
                messages.success(request, "用户已删除。")
        return redirect('users:user_management')
    
    # 处理 GET 请求列表展示与搜索
    q = request.GET.get('q', '').strip()
    users = User.objects.all().order_by('-date_joined')
    if q:
        # 使用 Q 对象进行跨字段 OR 模糊查询 (用户名 OR 姓名 OR 学号)
        users = users.filter(
            Q(username__icontains=q) | Q(real_name__icontains=q) | Q(student_id__icontains=q)
        )
    
    return render(request, 'users/user_management.html', {'users': users, 'q': q})


@login_required
def checkin_monitor(request):
    """
    签到实时监控视图
    - 管理员：可查看全平台所有活动的签到流水
    - 活动组织者：仅能查看自己发布的活动的签到记录
    - 支持按活动 ID 筛选
    """
    if not (request.user.role in ('admin', 'organizer') or request.user.is_superuser):
        messages.error(request, "您没有权限访问签到监控。")
        return redirect('activities:list')
    
    from activities.models import CheckIn, Activity
    activity_id = request.GET.get('activity', '')
    
    # 根据用户身份加载活动下拉筛选列表
    if request.user.role == 'admin' or request.user.is_superuser:
        activities = Activity.objects.all().order_by('-start_time')
    else:
        activities = Activity.objects.filter(organizer=request.user).order_by('-start_time')
    
    # 预加载外键关联对象，按签到时间倒序
    checkins = CheckIn.objects.select_related(
        'registration__user', 'registration__activity'
    ).order_by('-check_in_time')
    
    # 应用筛选条件
    if activity_id:
        checkins = checkins.filter(registration__activity_id=activity_id)
    elif request.user.role == 'organizer' and not request.user.is_superuser:
        checkins = checkins.filter(registration__activity__organizer=request.user)
    
    # 限制最新展示 100 条
    checkins = checkins[:100]
    
    return render(request, 'users/checkin_monitor.html', {
        'checkins': checkins,
        'activities': activities,
        'selected_activity': activity_id,
    })


# ----------------------------------------------------------------------
# 4. 数据报表导出功能（CSV / Excel）
# ----------------------------------------------------------------------

@login_required
def export_dashboard_csv(request):
    """
    管理员：将活动统计总表导出为 CSV 文件
    - 使用 utf-8-sig 编码防止 Excel 打开中文乱码
    """
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, "权限不足。")
        return redirect('activities:list')
    
    from activities.models import Activity
    
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="dashboard_stats.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['活动名称', '组织者', '开始时间', '状态', '报名人数', '最大人数'])
    
    # 使用 annotate 聚合统计有效报名人数
    for a in Activity.objects.annotate(
        reg_count=Count('registrations', filter=Q(registrations__status='registered'))
    ).order_by('-created_at'):
        writer.writerow([
            a.title,
            a.organizer.real_name or a.organizer.username,
            a.start_time.strftime('%Y-%m-%d %H:%M'),
            a.get_status_display(),
            a.reg_count,
            a.max_participants if a.max_participants else '不限',
        ])
    return response


@login_required
def export_dashboard_excel(request):
    """
    管理员：将活动统计报表导出为美化后的 Excel (.xlsx) 文件
    - 使用 openpyxl 进行单元格样式、表头背景色与列宽格式化
    """
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, "权限不足。")
        return redirect('activities:list')
    
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    from activities.models import Activity
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '活动统计'
    
    # 设置表头及样式
    headers = ['活动名称', '组织者', '开始时间', '状态', '报名人数', '最大人数']
    hf = PatternFill(start_color='0f3460', end_color='0f3460', fill_type='solid')
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=col, value=h)
        c.fill = hf
        c.font = Font(bold=True, color='FFFFFF')
        c.alignment = Alignment(horizontal='center')
        ws.column_dimensions[chr(64 + col)].width = 20
    
    # 写入活动数据行
    for a in Activity.objects.annotate(
        reg_count=Count('registrations', filter=Q(registrations__status='registered'))
    ).order_by('-created_at'):
        ws.append([
            a.title,
            a.organizer.real_name or a.organizer.username,
            a.start_time.strftime('%Y-%m-%d %H:%M'),
            a.get_status_display(),
            a.reg_count,
            a.max_participants if a.max_participants else '不限',
        ])
    
    # 输出到内存字节流并作为附件下载返回
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    response = HttpResponse(
        buf.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="dashboard_stats.xlsx"'
    return response


# ----------------------------------------------------------------------
# 5. 管理员数据统计大屏 (Admin Dashboard)
# ----------------------------------------------------------------------

@login_required
def admin_dashboard(request):
    """
    数据分析大屏与后台控制台
    - 统计全平台总用户量、活动数、有效报名量、签到总数
    - 统计各活动报名 Top 10
    - 统计用户角色分布比例
    - 统计最近 7 天的每日报名趋势数据
    """
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, "您没有权限访问管理后台。")
        return redirect('activities:list')

    from activities.models import Activity, Registration, CheckIn

    # 1. 基础指标统计 (卡片数据)
    total_users = User.objects.count()
    total_activities = Activity.objects.count()
    total_registrations = Registration.objects.filter(status='registered').count()
    total_checkins = CheckIn.objects.count()

    # 2. 热门活动 Top 10
    activity_stats = Activity.objects.annotate(
        reg_count=Count('registrations', filter=Q(registrations__status='registered'))
    ).order_by('-created_at')[:10]

    # 3. 角色分布饼图数据 (Group By role)
    role_stats = User.objects.values('role').annotate(count=Count('id'))

    # 4. 近 7 天每日报名量折线图数据
    today = timezone.now().date()
    reg_daily = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        count = Registration.objects.filter(
            registration_time__date=day,
            status='registered'
        ).count()
        reg_daily.append({'day': day.strftime('%m-%d'), 'count': count})

    context = {
        'total_users': total_users,
        'total_activities': total_activities,
        'total_registrations': total_registrations,
        'total_checkins': total_checkins,
        'activity_stats': activity_stats,
        'role_stats': list(role_stats),
        'reg_daily': reg_daily,
    }
    return render(request, 'users/admin_dashboard.html', context)

