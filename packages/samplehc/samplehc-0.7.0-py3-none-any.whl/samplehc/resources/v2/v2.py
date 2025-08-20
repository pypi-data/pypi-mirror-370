# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .hie.hie import (
    HieResource,
    AsyncHieResource,
    HieResourceWithRawResponse,
    AsyncHieResourceWithRawResponse,
    HieResourceWithStreamingResponse,
    AsyncHieResourceWithStreamingResponse,
)
from .database import (
    DatabaseResource,
    AsyncDatabaseResource,
    DatabaseResourceWithRawResponse,
    AsyncDatabaseResourceWithRawResponse,
    DatabaseResourceWithStreamingResponse,
    AsyncDatabaseResourceWithStreamingResponse,
)
from .policies import (
    PoliciesResource,
    AsyncPoliciesResource,
    PoliciesResourceWithRawResponse,
    AsyncPoliciesResourceWithRawResponse,
    PoliciesResourceWithStreamingResponse,
    AsyncPoliciesResourceWithStreamingResponse,
)
from ..._compat import cached_property
from .workflows import (
    WorkflowsResource,
    AsyncWorkflowsResource,
    WorkflowsResourceWithRawResponse,
    AsyncWorkflowsResourceWithRawResponse,
    WorkflowsResourceWithStreamingResponse,
    AsyncWorkflowsResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from .tasks.tasks import (
    TasksResource,
    AsyncTasksResource,
    TasksResourceWithRawResponse,
    AsyncTasksResourceWithRawResponse,
    TasksResourceWithStreamingResponse,
    AsyncTasksResourceWithStreamingResponse,
)
from .async_results import (
    AsyncResultsResource,
    AsyncAsyncResultsResource,
    AsyncResultsResourceWithRawResponse,
    AsyncAsyncResultsResourceWithRawResponse,
    AsyncResultsResourceWithStreamingResponse,
    AsyncAsyncResultsResourceWithStreamingResponse,
)
from .communication import (
    CommunicationResource,
    AsyncCommunicationResource,
    CommunicationResourceWithRawResponse,
    AsyncCommunicationResourceWithRawResponse,
    CommunicationResourceWithStreamingResponse,
    AsyncCommunicationResourceWithStreamingResponse,
)
from .events.events import (
    EventsResource,
    AsyncEventsResource,
    EventsResourceWithRawResponse,
    AsyncEventsResourceWithRawResponse,
    EventsResourceWithStreamingResponse,
    AsyncEventsResourceWithStreamingResponse,
)
from .ledger.ledger import (
    LedgerResource,
    AsyncLedgerResource,
    LedgerResourceWithRawResponse,
    AsyncLedgerResourceWithRawResponse,
    LedgerResourceWithStreamingResponse,
    AsyncLedgerResourceWithStreamingResponse,
)
from .browser_agents import (
    BrowserAgentsResource,
    AsyncBrowserAgentsResource,
    BrowserAgentsResourceWithRawResponse,
    AsyncBrowserAgentsResourceWithRawResponse,
    BrowserAgentsResourceWithStreamingResponse,
    AsyncBrowserAgentsResourceWithStreamingResponse,
)
from .documents.documents import (
    DocumentsResource,
    AsyncDocumentsResource,
    DocumentsResourceWithRawResponse,
    AsyncDocumentsResourceWithRawResponse,
    DocumentsResourceWithStreamingResponse,
    AsyncDocumentsResourceWithStreamingResponse,
)
from .integrations.integrations import (
    IntegrationsResource,
    AsyncIntegrationsResource,
    IntegrationsResourceWithRawResponse,
    AsyncIntegrationsResourceWithRawResponse,
    IntegrationsResourceWithStreamingResponse,
    AsyncIntegrationsResourceWithStreamingResponse,
)
from .clearinghouse.clearinghouse import (
    ClearinghouseResource,
    AsyncClearinghouseResource,
    ClearinghouseResourceWithRawResponse,
    AsyncClearinghouseResourceWithRawResponse,
    ClearinghouseResourceWithStreamingResponse,
    AsyncClearinghouseResourceWithStreamingResponse,
)
from .workflow_runs.workflow_runs import (
    WorkflowRunsResource,
    AsyncWorkflowRunsResource,
    WorkflowRunsResourceWithRawResponse,
    AsyncWorkflowRunsResourceWithRawResponse,
    WorkflowRunsResourceWithStreamingResponse,
    AsyncWorkflowRunsResourceWithStreamingResponse,
)
from .browser_automation.browser_automation import (
    BrowserAutomationResource,
    AsyncBrowserAutomationResource,
    BrowserAutomationResourceWithRawResponse,
    AsyncBrowserAutomationResourceWithRawResponse,
    BrowserAutomationResourceWithStreamingResponse,
    AsyncBrowserAutomationResourceWithStreamingResponse,
)

__all__ = ["V2Resource", "AsyncV2Resource"]


class V2Resource(SyncAPIResource):
    @cached_property
    def async_results(self) -> AsyncResultsResource:
        return AsyncResultsResource(self._client)

    @cached_property
    def workflow_runs(self) -> WorkflowRunsResource:
        return WorkflowRunsResource(self._client)

    @cached_property
    def tasks(self) -> TasksResource:
        return TasksResource(self._client)

    @cached_property
    def workflows(self) -> WorkflowsResource:
        return WorkflowsResource(self._client)

    @cached_property
    def documents(self) -> DocumentsResource:
        return DocumentsResource(self._client)

    @cached_property
    def communication(self) -> CommunicationResource:
        return CommunicationResource(self._client)

    @cached_property
    def clearinghouse(self) -> ClearinghouseResource:
        return ClearinghouseResource(self._client)

    @cached_property
    def ledger(self) -> LedgerResource:
        return LedgerResource(self._client)

    @cached_property
    def integrations(self) -> IntegrationsResource:
        return IntegrationsResource(self._client)

    @cached_property
    def events(self) -> EventsResource:
        return EventsResource(self._client)

    @cached_property
    def browser_agents(self) -> BrowserAgentsResource:
        return BrowserAgentsResource(self._client)

    @cached_property
    def policies(self) -> PoliciesResource:
        return PoliciesResource(self._client)

    @cached_property
    def hie(self) -> HieResource:
        return HieResource(self._client)

    @cached_property
    def database(self) -> DatabaseResource:
        return DatabaseResource(self._client)

    @cached_property
    def browser_automation(self) -> BrowserAutomationResource:
        return BrowserAutomationResource(self._client)

    @cached_property
    def with_raw_response(self) -> V2ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return V2ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> V2ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return V2ResourceWithStreamingResponse(self)


class AsyncV2Resource(AsyncAPIResource):
    @cached_property
    def async_results(self) -> AsyncAsyncResultsResource:
        return AsyncAsyncResultsResource(self._client)

    @cached_property
    def workflow_runs(self) -> AsyncWorkflowRunsResource:
        return AsyncWorkflowRunsResource(self._client)

    @cached_property
    def tasks(self) -> AsyncTasksResource:
        return AsyncTasksResource(self._client)

    @cached_property
    def workflows(self) -> AsyncWorkflowsResource:
        return AsyncWorkflowsResource(self._client)

    @cached_property
    def documents(self) -> AsyncDocumentsResource:
        return AsyncDocumentsResource(self._client)

    @cached_property
    def communication(self) -> AsyncCommunicationResource:
        return AsyncCommunicationResource(self._client)

    @cached_property
    def clearinghouse(self) -> AsyncClearinghouseResource:
        return AsyncClearinghouseResource(self._client)

    @cached_property
    def ledger(self) -> AsyncLedgerResource:
        return AsyncLedgerResource(self._client)

    @cached_property
    def integrations(self) -> AsyncIntegrationsResource:
        return AsyncIntegrationsResource(self._client)

    @cached_property
    def events(self) -> AsyncEventsResource:
        return AsyncEventsResource(self._client)

    @cached_property
    def browser_agents(self) -> AsyncBrowserAgentsResource:
        return AsyncBrowserAgentsResource(self._client)

    @cached_property
    def policies(self) -> AsyncPoliciesResource:
        return AsyncPoliciesResource(self._client)

    @cached_property
    def hie(self) -> AsyncHieResource:
        return AsyncHieResource(self._client)

    @cached_property
    def database(self) -> AsyncDatabaseResource:
        return AsyncDatabaseResource(self._client)

    @cached_property
    def browser_automation(self) -> AsyncBrowserAutomationResource:
        return AsyncBrowserAutomationResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncV2ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncV2ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncV2ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncV2ResourceWithStreamingResponse(self)


class V2ResourceWithRawResponse:
    def __init__(self, v2: V2Resource) -> None:
        self._v2 = v2

    @cached_property
    def async_results(self) -> AsyncResultsResourceWithRawResponse:
        return AsyncResultsResourceWithRawResponse(self._v2.async_results)

    @cached_property
    def workflow_runs(self) -> WorkflowRunsResourceWithRawResponse:
        return WorkflowRunsResourceWithRawResponse(self._v2.workflow_runs)

    @cached_property
    def tasks(self) -> TasksResourceWithRawResponse:
        return TasksResourceWithRawResponse(self._v2.tasks)

    @cached_property
    def workflows(self) -> WorkflowsResourceWithRawResponse:
        return WorkflowsResourceWithRawResponse(self._v2.workflows)

    @cached_property
    def documents(self) -> DocumentsResourceWithRawResponse:
        return DocumentsResourceWithRawResponse(self._v2.documents)

    @cached_property
    def communication(self) -> CommunicationResourceWithRawResponse:
        return CommunicationResourceWithRawResponse(self._v2.communication)

    @cached_property
    def clearinghouse(self) -> ClearinghouseResourceWithRawResponse:
        return ClearinghouseResourceWithRawResponse(self._v2.clearinghouse)

    @cached_property
    def ledger(self) -> LedgerResourceWithRawResponse:
        return LedgerResourceWithRawResponse(self._v2.ledger)

    @cached_property
    def integrations(self) -> IntegrationsResourceWithRawResponse:
        return IntegrationsResourceWithRawResponse(self._v2.integrations)

    @cached_property
    def events(self) -> EventsResourceWithRawResponse:
        return EventsResourceWithRawResponse(self._v2.events)

    @cached_property
    def browser_agents(self) -> BrowserAgentsResourceWithRawResponse:
        return BrowserAgentsResourceWithRawResponse(self._v2.browser_agents)

    @cached_property
    def policies(self) -> PoliciesResourceWithRawResponse:
        return PoliciesResourceWithRawResponse(self._v2.policies)

    @cached_property
    def hie(self) -> HieResourceWithRawResponse:
        return HieResourceWithRawResponse(self._v2.hie)

    @cached_property
    def database(self) -> DatabaseResourceWithRawResponse:
        return DatabaseResourceWithRawResponse(self._v2.database)

    @cached_property
    def browser_automation(self) -> BrowserAutomationResourceWithRawResponse:
        return BrowserAutomationResourceWithRawResponse(self._v2.browser_automation)


class AsyncV2ResourceWithRawResponse:
    def __init__(self, v2: AsyncV2Resource) -> None:
        self._v2 = v2

    @cached_property
    def async_results(self) -> AsyncAsyncResultsResourceWithRawResponse:
        return AsyncAsyncResultsResourceWithRawResponse(self._v2.async_results)

    @cached_property
    def workflow_runs(self) -> AsyncWorkflowRunsResourceWithRawResponse:
        return AsyncWorkflowRunsResourceWithRawResponse(self._v2.workflow_runs)

    @cached_property
    def tasks(self) -> AsyncTasksResourceWithRawResponse:
        return AsyncTasksResourceWithRawResponse(self._v2.tasks)

    @cached_property
    def workflows(self) -> AsyncWorkflowsResourceWithRawResponse:
        return AsyncWorkflowsResourceWithRawResponse(self._v2.workflows)

    @cached_property
    def documents(self) -> AsyncDocumentsResourceWithRawResponse:
        return AsyncDocumentsResourceWithRawResponse(self._v2.documents)

    @cached_property
    def communication(self) -> AsyncCommunicationResourceWithRawResponse:
        return AsyncCommunicationResourceWithRawResponse(self._v2.communication)

    @cached_property
    def clearinghouse(self) -> AsyncClearinghouseResourceWithRawResponse:
        return AsyncClearinghouseResourceWithRawResponse(self._v2.clearinghouse)

    @cached_property
    def ledger(self) -> AsyncLedgerResourceWithRawResponse:
        return AsyncLedgerResourceWithRawResponse(self._v2.ledger)

    @cached_property
    def integrations(self) -> AsyncIntegrationsResourceWithRawResponse:
        return AsyncIntegrationsResourceWithRawResponse(self._v2.integrations)

    @cached_property
    def events(self) -> AsyncEventsResourceWithRawResponse:
        return AsyncEventsResourceWithRawResponse(self._v2.events)

    @cached_property
    def browser_agents(self) -> AsyncBrowserAgentsResourceWithRawResponse:
        return AsyncBrowserAgentsResourceWithRawResponse(self._v2.browser_agents)

    @cached_property
    def policies(self) -> AsyncPoliciesResourceWithRawResponse:
        return AsyncPoliciesResourceWithRawResponse(self._v2.policies)

    @cached_property
    def hie(self) -> AsyncHieResourceWithRawResponse:
        return AsyncHieResourceWithRawResponse(self._v2.hie)

    @cached_property
    def database(self) -> AsyncDatabaseResourceWithRawResponse:
        return AsyncDatabaseResourceWithRawResponse(self._v2.database)

    @cached_property
    def browser_automation(self) -> AsyncBrowserAutomationResourceWithRawResponse:
        return AsyncBrowserAutomationResourceWithRawResponse(self._v2.browser_automation)


class V2ResourceWithStreamingResponse:
    def __init__(self, v2: V2Resource) -> None:
        self._v2 = v2

    @cached_property
    def async_results(self) -> AsyncResultsResourceWithStreamingResponse:
        return AsyncResultsResourceWithStreamingResponse(self._v2.async_results)

    @cached_property
    def workflow_runs(self) -> WorkflowRunsResourceWithStreamingResponse:
        return WorkflowRunsResourceWithStreamingResponse(self._v2.workflow_runs)

    @cached_property
    def tasks(self) -> TasksResourceWithStreamingResponse:
        return TasksResourceWithStreamingResponse(self._v2.tasks)

    @cached_property
    def workflows(self) -> WorkflowsResourceWithStreamingResponse:
        return WorkflowsResourceWithStreamingResponse(self._v2.workflows)

    @cached_property
    def documents(self) -> DocumentsResourceWithStreamingResponse:
        return DocumentsResourceWithStreamingResponse(self._v2.documents)

    @cached_property
    def communication(self) -> CommunicationResourceWithStreamingResponse:
        return CommunicationResourceWithStreamingResponse(self._v2.communication)

    @cached_property
    def clearinghouse(self) -> ClearinghouseResourceWithStreamingResponse:
        return ClearinghouseResourceWithStreamingResponse(self._v2.clearinghouse)

    @cached_property
    def ledger(self) -> LedgerResourceWithStreamingResponse:
        return LedgerResourceWithStreamingResponse(self._v2.ledger)

    @cached_property
    def integrations(self) -> IntegrationsResourceWithStreamingResponse:
        return IntegrationsResourceWithStreamingResponse(self._v2.integrations)

    @cached_property
    def events(self) -> EventsResourceWithStreamingResponse:
        return EventsResourceWithStreamingResponse(self._v2.events)

    @cached_property
    def browser_agents(self) -> BrowserAgentsResourceWithStreamingResponse:
        return BrowserAgentsResourceWithStreamingResponse(self._v2.browser_agents)

    @cached_property
    def policies(self) -> PoliciesResourceWithStreamingResponse:
        return PoliciesResourceWithStreamingResponse(self._v2.policies)

    @cached_property
    def hie(self) -> HieResourceWithStreamingResponse:
        return HieResourceWithStreamingResponse(self._v2.hie)

    @cached_property
    def database(self) -> DatabaseResourceWithStreamingResponse:
        return DatabaseResourceWithStreamingResponse(self._v2.database)

    @cached_property
    def browser_automation(self) -> BrowserAutomationResourceWithStreamingResponse:
        return BrowserAutomationResourceWithStreamingResponse(self._v2.browser_automation)


class AsyncV2ResourceWithStreamingResponse:
    def __init__(self, v2: AsyncV2Resource) -> None:
        self._v2 = v2

    @cached_property
    def async_results(self) -> AsyncAsyncResultsResourceWithStreamingResponse:
        return AsyncAsyncResultsResourceWithStreamingResponse(self._v2.async_results)

    @cached_property
    def workflow_runs(self) -> AsyncWorkflowRunsResourceWithStreamingResponse:
        return AsyncWorkflowRunsResourceWithStreamingResponse(self._v2.workflow_runs)

    @cached_property
    def tasks(self) -> AsyncTasksResourceWithStreamingResponse:
        return AsyncTasksResourceWithStreamingResponse(self._v2.tasks)

    @cached_property
    def workflows(self) -> AsyncWorkflowsResourceWithStreamingResponse:
        return AsyncWorkflowsResourceWithStreamingResponse(self._v2.workflows)

    @cached_property
    def documents(self) -> AsyncDocumentsResourceWithStreamingResponse:
        return AsyncDocumentsResourceWithStreamingResponse(self._v2.documents)

    @cached_property
    def communication(self) -> AsyncCommunicationResourceWithStreamingResponse:
        return AsyncCommunicationResourceWithStreamingResponse(self._v2.communication)

    @cached_property
    def clearinghouse(self) -> AsyncClearinghouseResourceWithStreamingResponse:
        return AsyncClearinghouseResourceWithStreamingResponse(self._v2.clearinghouse)

    @cached_property
    def ledger(self) -> AsyncLedgerResourceWithStreamingResponse:
        return AsyncLedgerResourceWithStreamingResponse(self._v2.ledger)

    @cached_property
    def integrations(self) -> AsyncIntegrationsResourceWithStreamingResponse:
        return AsyncIntegrationsResourceWithStreamingResponse(self._v2.integrations)

    @cached_property
    def events(self) -> AsyncEventsResourceWithStreamingResponse:
        return AsyncEventsResourceWithStreamingResponse(self._v2.events)

    @cached_property
    def browser_agents(self) -> AsyncBrowserAgentsResourceWithStreamingResponse:
        return AsyncBrowserAgentsResourceWithStreamingResponse(self._v2.browser_agents)

    @cached_property
    def policies(self) -> AsyncPoliciesResourceWithStreamingResponse:
        return AsyncPoliciesResourceWithStreamingResponse(self._v2.policies)

    @cached_property
    def hie(self) -> AsyncHieResourceWithStreamingResponse:
        return AsyncHieResourceWithStreamingResponse(self._v2.hie)

    @cached_property
    def database(self) -> AsyncDatabaseResourceWithStreamingResponse:
        return AsyncDatabaseResourceWithStreamingResponse(self._v2.database)

    @cached_property
    def browser_automation(self) -> AsyncBrowserAutomationResourceWithStreamingResponse:
        return AsyncBrowserAutomationResourceWithStreamingResponse(self._v2.browser_automation)
