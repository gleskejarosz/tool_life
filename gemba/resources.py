from import_export import resources
from .models import JobModel2


class JobModelResource(resources.ModelResource):
    class Meta:
        model = JobModel2
