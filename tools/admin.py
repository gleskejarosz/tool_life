from django.contrib import admin

from tools.models import JobModel, JobUpdate, MachineModel, OperationModel, RelationModel, StationModel, ToolModel

admin.site.register(JobModel)
admin.site.register(JobUpdate)
admin.site.register(MachineModel)
admin.site.register(OperationModel)
admin.site.register(RelationModel)
admin.site.register(StationModel)
admin.site.register(ToolModel)
