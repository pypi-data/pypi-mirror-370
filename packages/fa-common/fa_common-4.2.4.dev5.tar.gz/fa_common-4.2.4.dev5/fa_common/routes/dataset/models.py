# from typing import Union

# from fa_common import CamelModel
# from fa_common.serializers import Serializer, patch

# from gpt_backend.aem import AEMProjectSZ
# from gpt_backend.sensi import SensiProjectSZ
# from fa_common.routes.shared import GenericProject, Project


# @patch
# class ProjectSZ(Serializer):
#     class Meta:
#         model = Project
#         read_only_fields = {"id", "user_id"}


# @patch
# class GenericProjectSZ(Serializer):
#     class Meta:
#         model = GenericProject
#         read_only_fields = {"id", "user_id"}


# class CreateProjectRequest(CamelModel):
#     override: bool = False
#     project: Union[AEMProjectSZ, SensiProjectSZ, GenericProjectSZ]
