from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from iam.models import SysGroup, SysUser, SysUserGroup

User = get_user_model()


class Command(BaseCommand):
    help = "初始化CMDB角色（管理员/运维/只读），可选创建联调测试用户并绑定角色"

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-demo-users",
            action="store_true",
            help="同时创建测试用户：admin_user/ops_user/readonly_user",
        )
        parser.add_argument(
            "--password",
            default="Cmdb@123",
            help="测试用户统一密码，默认 Cmdb@123",
        )

    def handle(self, *args, **options):
        with_demo_users = options["with_demo_users"]
        password = options["password"]

        role_groups = {
            "管理员": "admin_user",
            "运维": "ops_user",
            "只读": "readonly_user",
        }

        created_groups = 0
        for group_name in role_groups:
            _, created = SysGroup.objects.get_or_create(
                group_name=group_name,
                defaults={"description": f"{group_name}角色", "status": "active"},
            )
            if created:
                created_groups += 1

        self.stdout.write(self.style.SUCCESS(f"角色初始化完成，新增用户组 {created_groups} 个。"))

        if not with_demo_users:
            self.stdout.write("未选择创建测试用户，命令执行结束。")
            return

        created_users = 0
        for group_name, username in role_groups.items():
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    "is_active": True,
                    "is_staff": True,
                    "email": f"{username}@cmdb.local",
                },
            )
            if user_created:
                user.set_password(password)
                if group_name == "管理员":
                    user.is_superuser = True
                user.save()
                created_users += 1

            SysUser.objects.get_or_create(
                user=user,
                defaults={
                    "display_name": username,
                    "phone": "",
                    "status": "active",
                },
            )

            group = SysGroup.objects.get(group_name=group_name)
            SysUserGroup.objects.get_or_create(user=user, group=group)

        self.stdout.write(self.style.SUCCESS(f"测试用户处理完成，新增用户 {created_users} 个。"))
        self.stdout.write(self.style.WARNING("默认测试账号：admin_user / ops_user / readonly_user"))
        self.stdout.write(self.style.WARNING("请尽快修改默认密码或在生产环境禁用测试账号。"))
