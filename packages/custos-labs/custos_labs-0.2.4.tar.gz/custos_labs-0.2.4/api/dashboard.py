# api/dashboard

from admin_tools.dashboard import modules, Dashboard

class CustomIndexDashboard(Dashboard):
    def init_with_context(self, context):
        self.children.append(modules.ModelList(
            'User Management',
            models=['auth.User', 'api.Profile'],
        ))
        self.children.append(modules.ModelList(
            'API & Usage',
            models=['api.APIKey', 'api.APIUsageLog', 'api.UserActivityLog'],
        ))
        self.children.append(modules.RecentActions('Recent Actions', 10))
