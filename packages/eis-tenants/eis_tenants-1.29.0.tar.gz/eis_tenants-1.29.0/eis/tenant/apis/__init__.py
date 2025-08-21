
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from eis.tenant.api.custom_schema_api import CustomSchemaApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from eis.tenant.api.custom_schema_api import CustomSchemaApi
from eis.tenant.api.dashboard_api import DashboardApi
from eis.tenant.api.dashboard_group_api import DashboardGroupApi
from eis.tenant.api.data_report_api import DataReportApi
from eis.tenant.api.data_report_executor_api import DataReportExecutorApi
from eis.tenant.api.delete_organization_invitations_api import DeleteOrganizationInvitationsApi
from eis.tenant.api.health_check_api import HealthCheckApi
from eis.tenant.api.invite_organizations_api import InviteOrganizationsApi
from eis.tenant.api.invite_users_api import InviteUsersApi
from eis.tenant.api.list_organization_invitations_api import ListOrganizationInvitationsApi
from eis.tenant.api.organization_migration_api import OrganizationMigrationApi
from eis.tenant.api.organizations_api import OrganizationsApi
from eis.tenant.api.re_invite_an_organization_api import ReInviteAnOrganizationApi
from eis.tenant.api.roles_api import RolesApi
from eis.tenant.api.settings_api import SettingsApi
from eis.tenant.api.users_api import UsersApi
