from typing import List, TypedDict

from dixa.api import DixaResource, DixaVersion
from dixa.exceptions import DixaAPIError
from dixa.model.v1.agent import AgentPresence
from dixa.model.v1.team import Team1, TeamMember


class TeamAddMembersBody(TypedDict):
    agentIds: List[str]


class TeamRemoveMembersBody(TypedDict):
    agentIds: List[str]


class TeamCreateBody(TypedDict):
    name: str


class TeamResource(DixaResource):
    """
    https://docs.dixa.io/openapi/dixa-api/v1/tag/Teams/
    """

    resource = "teams"
    dixa_version: DixaVersion = "v1"

    def add_members(self, team_id: str, body: TeamAddMembersBody):
        """Add members to a team.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Teams/#tag/Teams/operation/patchTeamsTeamidAgents
        """
        return self.client.post(f"{self._url}/{team_id}/agents", body)

    def create(self, body: TeamCreateBody) -> Team1:
        """Create a team.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Teams/#tag/Teams/operation/postTeams
        """
        data = self.client.post(self._url, body)
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return Team1(**data)

    def delete(self, team_id: str):
        """Delete a team by ID.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Teams/#tag/Teams/operation/deleteTeamsTeamid
        """
        return self.client.delete(f"{self._url}/{team_id}")

    def get(self, team_id: str) -> Team1:
        """Get a team by ID.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Teams/#tag/Teams/operation/getTeamsTeamid
        """
        data = self.client.get(f"{self._url}/{team_id}")
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return Team1(**data)

    def list_members(self, team_id: str) -> List[TeamMember]:
        """List members of a team.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Teams/#tag/Teams/operation/getTeamsTeamidAgents
        """
        return self.client.paginate(f"{self._url}/{team_id}/agents")

    def list_presence(self, team_id: str) -> List[AgentPresence]:
        """List presence of a team.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Teams/#tag/Teams/operation/getTeamsTeamidPresence
        """
        return self.client.paginate(f"{self._url}/{team_id}/presence")

    def list_(self) -> List[Team1]:
        """List teams.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Teams/#tag/Teams/operation/getTeams
        """
        return self.client.paginate(self._url)

    def remove_members(self, team_id: str, body: TeamRemoveMembersBody):
        """Remove members from a team.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Teams/#tag/Teams/operation/deleteTeamsTeamidAgents
        """
        return self.client.delete(f"{self._url}/{team_id}/agents", body)
