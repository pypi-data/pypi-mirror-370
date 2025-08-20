# pyright: reportImportCycles=false
from typing import Literal, Unpack, overload

from loguru import logger
from notte_core import enable_nest_asyncio
from notte_core.actions import GotoAction
from notte_core.common.config import LlmModel, PerceptionType
from notte_core.data.space import ImageData, StructuredData, TBaseModel
from pydantic import BaseModel
from typing_extensions import final

from notte_sdk.endpoints.agents import AgentsClient, BatchAgentFactory, RemoteAgentFactory
from notte_sdk.endpoints.files import FileStorageClient, RemoteFileStorageFactory
from notte_sdk.endpoints.personas import PersonasClient, RemotePersonaFactory
from notte_sdk.endpoints.sessions import RemoteSessionFactory, SessionsClient, SessionViewerType
from notte_sdk.endpoints.vaults import RemoteVaultFactory, VaultsClient
from notte_sdk.endpoints.workflows import RemoteWorkflowFactory, WorkflowsClient
from notte_sdk.types import ScrapeMarkdownParamsDict, ScrapeRequestDict

enable_nest_asyncio()


@final
class NotteClient:
    """
    Client for the Notte API.

    Note: this client is only able to handle one session at a time.
    If you need to handle multiple sessions, you need to create a new client for each session.
    """

    def __init__(
        self,
        api_key: str | None = None,
        server_url: str | None = None,
        verbose: bool = False,
        viewer_type: SessionViewerType = SessionViewerType.BROWSER,
    ):
        """Initialize a NotteClient instance.

        Initializes the NotteClient with the specified API key and server URL, creating instances
        of SessionsClient, AgentsClient, VaultsClient, and PersonasClient.

        Args:
            api_key: Optional API key for authentication.
        """

        self.sessions: SessionsClient = SessionsClient(
            root_client=self, api_key=api_key, server_url=server_url, verbose=verbose, viewer_type=viewer_type
        )
        self.agents: AgentsClient = AgentsClient(
            root_client=self, api_key=api_key, server_url=server_url, verbose=verbose
        )
        self.personas: PersonasClient = PersonasClient(
            root_client=self, api_key=api_key, server_url=server_url, verbose=verbose
        )
        self.vaults: VaultsClient = VaultsClient(
            root_client=self, api_key=api_key, server_url=server_url, verbose=verbose
        )
        self.files: FileStorageClient = FileStorageClient(
            root_client=self, api_key=api_key, server_url=server_url, verbose=verbose
        )
        self.workflows: WorkflowsClient = WorkflowsClient(
            root_client=self, api_key=api_key, server_url=server_url, verbose=verbose
        )

        if self.sessions.server_url != self.sessions.DEFAULT_NOTTE_API_URL:
            logger.warning(f"NOTTE_API_URL is set to: {self.sessions.server_url}")
        self.models: type[LlmModel] = LlmModel

    def health_check(self) -> None:
        """
        Health check the Notte API.
        """
        return self.sessions.health_check()

    @property
    def Agent(self) -> RemoteAgentFactory:
        return RemoteAgentFactory(self.agents)

    @property
    def BatchAgent(self) -> BatchAgentFactory:
        return BatchAgentFactory(self.agents)

    @property
    def Session(self) -> RemoteSessionFactory:
        return RemoteSessionFactory(self.sessions)

    @property
    def Vault(self) -> RemoteVaultFactory:
        return RemoteVaultFactory(self.vaults)

    @property
    def Persona(self) -> RemotePersonaFactory:
        return RemotePersonaFactory(self.personas, self.vaults)

    @property
    def FileStorage(self) -> RemoteFileStorageFactory:
        return RemoteFileStorageFactory(self.files)

    @property
    def Workflow(self) -> RemoteWorkflowFactory:
        return RemoteWorkflowFactory(self)

    @overload
    def scrape(self, /, url: str, **params: Unpack[ScrapeMarkdownParamsDict]) -> str: ...

    @overload
    def scrape(  # pyright: ignore [reportOverlappingOverload]
        self,
        /,
        url: str,
        *,
        instructions: str,
        **params: Unpack[ScrapeMarkdownParamsDict],
    ) -> StructuredData[BaseModel]: ...

    @overload
    def scrape(  # pyright: ignore [reportOverlappingOverload]
        self,
        /,
        url: str,
        *,
        response_format: type[TBaseModel],
        instructions: str | None = None,
        **params: Unpack[ScrapeMarkdownParamsDict],
    ) -> StructuredData[TBaseModel]: ...

    @overload
    def scrape(self, /, url: str, *, only_images: Literal[True]) -> list[ImageData]: ...  # pyright: ignore [reportOverlappingOverload]

    def scrape(
        self, /, url: str, **data: Unpack[ScrapeRequestDict]
    ) -> str | StructuredData[BaseModel] | list[ImageData]:
        with self.Session(headless=True, perception_type=PerceptionType.FAST) as session:
            result = session.execute(GotoAction(url=url))
            if not result.success and result.exception is not None:
                raise result.exception
            return session.scrape(**data)
