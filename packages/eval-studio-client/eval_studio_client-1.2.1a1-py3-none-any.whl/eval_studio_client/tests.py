import dataclasses
import datetime
import enum
import json
import time
from typing import Any
from typing import List
from typing import Optional
from typing import Union

from eval_studio_client import api
from eval_studio_client import documents as d7s
from eval_studio_client import perturbators as p10s
from eval_studio_client import utils
from eval_studio_client.api import models
from eval_studio_client.api.models import (
    test_service_clone_test_request as clone_test_request,
)


class TestCaseGenerator(enum.Enum):
    """Methods used for test case generation."""

    unspecified = models.V1TestCasesGenerator.TEST_CASES_GENERATOR_UNSPECIFIED
    simple_factual_questions = (
        models.V1TestCasesGenerator.TEST_CASES_GENERATOR_SIMPLE_FACTUAL_QUESTIONS
    )
    multi_hop_questions = (
        models.V1TestCasesGenerator.TEST_CASES_GENERATOR_MULTI_HOP_QUESTIONS
    )
    inference_questions = (
        models.V1TestCasesGenerator.TEST_CASES_GENERATOR_INFERENCE_QUESTIONS
    )
    numerical_reasoning_questions = (
        models.V1TestCasesGenerator.TEST_CASES_GENERATOR_NUMERICAL_REASONING_QUESTIONS
    )
    ambiguity_handling_questions = (
        models.V1TestCasesGenerator.TEST_CASES_GENERATOR_AMBIGUITY_HANDLING_QUESTIONS
    )
    negation_and_contradiction_questions = (
        models.V1TestCasesGenerator.TEST_CASES_GENERATOR_NEGATION_AND_CONTRADICTION_QUESTIONS
    )
    temporal_reasoning_questions = (
        models.V1TestCasesGenerator.TEST_CASES_GENERATOR_TEMPORAL_REASONING_QUESTIONS
    )
    out_of_scope_questions = (
        models.V1TestCasesGenerator.TEST_CASES_GENERATOR_OUT_OF_SCOPE_QUESTIONS
    )
    yes_or_no_questions = (
        models.V1TestCasesGenerator.TEST_CASES_GENERATOR_YES_OR_NO_QUESTIONS
    )
    multiple_choice_questions = (
        models.V1TestCasesGenerator.TEST_CASES_GENERATOR_MULTIPLE_CHOICE_QUESTIONS
    )
    demographic_representation_questions = (
        models.V1TestCasesGenerator.TEST_CASES_GENERATOR_DEMOGRAPHIC_REPRESENTATION_QUESTIONS
    )
    sentiment_variation_questions = (
        models.V1TestCasesGenerator.TEST_CASES_GENERATOR_SENTIMENT_VARIATION_QUESTIONS
    )
    irrelevant_information_questions = (
        models.V1TestCasesGenerator.TEST_CASES_GENERATOR_IRRELEVANT_INFORMATION_QUESTIONS
    )
    deliberately_misleading_questions = (
        models.V1TestCasesGenerator.TEST_CASES_GENERATOR_DELIBERATELY_MISLEADING_QUESTIONS
    )

    def to_api_proto(self) -> models.V1TestCasesGenerator:
        """Converts the client TestCaseGenerator to an API TestCaseGeneration."""
        proto_values = {
            TestCaseGenerator.unspecified: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_UNSPECIFIED,
            TestCaseGenerator.simple_factual_questions: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_SIMPLE_FACTUAL_QUESTIONS,
            TestCaseGenerator.multi_hop_questions: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_MULTI_HOP_QUESTIONS,
            TestCaseGenerator.inference_questions: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_INFERENCE_QUESTIONS,
            TestCaseGenerator.numerical_reasoning_questions: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_NUMERICAL_REASONING_QUESTIONS,
            TestCaseGenerator.ambiguity_handling_questions: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_AMBIGUITY_HANDLING_QUESTIONS,
            TestCaseGenerator.negation_and_contradiction_questions: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_NEGATION_AND_CONTRADICTION_QUESTIONS,
            TestCaseGenerator.temporal_reasoning_questions: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_TEMPORAL_REASONING_QUESTIONS,
            TestCaseGenerator.out_of_scope_questions: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_OUT_OF_SCOPE_QUESTIONS,
            TestCaseGenerator.yes_or_no_questions: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_YES_OR_NO_QUESTIONS,
            TestCaseGenerator.multiple_choice_questions: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_MULTIPLE_CHOICE_QUESTIONS,
            TestCaseGenerator.demographic_representation_questions: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_DEMOGRAPHIC_REPRESENTATION_QUESTIONS,
            TestCaseGenerator.sentiment_variation_questions: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_SENTIMENT_VARIATION_QUESTIONS,
            TestCaseGenerator.irrelevant_information_questions: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_IRRELEVANT_INFORMATION_QUESTIONS,
            TestCaseGenerator.deliberately_misleading_questions: models.V1TestCasesGenerator.TEST_CASES_GENERATOR_DELIBERATELY_MISLEADING_QUESTIONS,
        }

        return proto_values[self]


@dataclasses.dataclass
class _TestCaseGenerationHandle:
    name: Any | None
    progress: Optional[float] = None
    progress_message: Optional[str] = None
    error: Optional[models.RpcStatus] = None
    done: Optional[bool] = None

    @staticmethod
    def _from_operation(
        res: models.V1GenerateTestCasesResponse | models.V1GetOperationResponse,
    ) -> "_TestCaseGenerationHandle":
        """Converts an API operation to prompt generation handle."""
        op: models.V1Operation | None = res.operation
        if not op:
            return _TestCaseGenerationHandle(name=None)

        # progress
        if hasattr(op, "metadata") and op.metadata:
            meta_dict = op.metadata.to_dict() or {}
        else:
            meta_dict = {}

        return _TestCaseGenerationHandle(
            name=op.name,
            progress=meta_dict.get("progress"),
            progress_message=meta_dict.get("progressMessage"),
            error=op.error,
            done=op.done,
        )


@dataclasses.dataclass
class _TestCaseLibraryGetHandle(_TestCaseGenerationHandle):
    @staticmethod
    def _from_operation(
        res: (
            models.V1ImportTestCasesFromLibraryResponse | models.V1GetOperationResponse
        ),
    ) -> "_TestCaseLibraryGetHandle":
        """Converts an API operation to prompt library handle."""
        op: models.V1Operation | None = res.operation
        if not op:
            return _TestCaseLibraryGetHandle(name=None)

        # progress
        if hasattr(op, "metadata") and op.metadata:
            meta_dict = op.metadata.to_dict() or {}
        else:
            meta_dict = {}

        return _TestCaseLibraryGetHandle(
            name=op.name,
            progress=meta_dict.get("progress"),
            progress_message=meta_dict.get("progressMessage"),
            error=op.error,
            done=op.done,
        )


@dataclasses.dataclass
class TestCaseLibraryItem:
    """Represents a single test case library item - test suite."""

    key: str
    name: str
    description: str
    test_suite_url: str
    test_count: int
    test_case_count: int
    evaluates: List[str]
    categories: List[str]

    @staticmethod
    def _from_api_items(
        api_items: List[models.V1PromptLibraryItem],
    ) -> List["TestCaseLibraryItem"]:
        return (
            [
                TestCaseLibraryItem(
                    key=api_item.name or "",
                    name=api_item.display_name or "",
                    description=api_item.description or "",
                    test_suite_url=api_item.test_suite_url or "",
                    test_count=api_item.test_count or 0,
                    test_case_count=api_item.test_case_count or 0,
                    evaluates=list(api_item.evaluates) if api_item.evaluates else [],
                    categories=list(api_item.categories) if api_item.categories else [],
                )
                for api_item in api_items
            ]
            if api_items
            else []
        )


@dataclasses.dataclass
class TestCase:
    """Represents a single test case, which contains tested prompt, expected answer
    and set of constraints.

    Attributes:
        key (str): Generated ID of the test case.
        prompt (str): Prompt of the test case.
        answer (str): Expected answer of the test case.
        constraints (List[str]): String tokens expected in the actual answer.
            Note: all of the constraints in the list are concatenated using AND
            operator, which means actual answer need to contain all of the tokens.
        create_time (datetime): Timestamp of the test case creation.
        update_time (datetime): Timestamp of the last test case update.
    """

    key: str
    prompt: str
    answer: str
    constraints: List[str]
    condition: str
    create_time: Optional[datetime.datetime] = None
    update_time: Optional[datetime.datetime] = None

    def to_api_proto(self) -> models.V1TestCase:
        """Converts the client TestCase to an API TestCase."""
        return models.V1TestCase(
            prompt=self.prompt,
            answer=self.answer,
            constraints=self.constraints,
            condition=self.condition,
        )

    @staticmethod
    def _from_api_test_case(api_test_case: models.V1TestCase) -> "TestCase":
        return TestCase(
            key=api_test_case.name or "",
            prompt=api_test_case.prompt or "",
            answer=api_test_case.answer or "",
            constraints=api_test_case.constraints or [],
            condition=api_test_case.condition or "",
        )


@dataclasses.dataclass
class TestCaseRelationship:
    source_test_case_key: str
    target_test_case_key: str
    relationship_type: str

    def to_api_proto(self) -> models.V1TestCaseRelationship:
        """Converts the client TestCase to an API TestCase."""
        return models.V1TestCaseRelationship(
            source=self.source_test_case_key,
            target=self.target_test_case_key,
            type=self.relationship_type,
        )

    @staticmethod
    def _from_api_test_case_rel(
        api_test_case_rel: models.V1TestCaseRelationship,
    ) -> "TestCaseRelationship":
        return TestCaseRelationship(
            source_test_case_key=api_test_case_rel.source or "",
            target_test_case_key=api_test_case_rel.target or "",
            relationship_type=api_test_case_rel.type or "",
        )


@dataclasses.dataclass
class Test:
    """Represents a test, which contains a set of test cases and optionally
    also documents for evaluating RAG systems.

    Attributes:
        key (str): Generated ID of the test.
        name (str): Name of the test.
        description (str): Description of the test.
        create_time (datetime): Timestamp of the test creation.
        update_time (datetime): Timestamp of the last test update.
    """

    key: str
    name: str
    description: str
    _document_names: List[str]
    create_time: Optional[datetime.datetime] = None
    update_time: Optional[datetime.datetime] = None
    _client: Optional[api.ApiClient] = None
    _gen_tc_op_name: Optional[str] = None
    _lib_tc_op_name: Optional[str] = None

    def __post_init__(self):
        if self._client:
            self._test_api = api.TestServiceApi(self._client)
            self._test_case_api = api.TestCaseServiceApi(self._client)
            self._document_api = api.DocumentServiceApi(self._client)
            self._operation_api = api.OperationServiceApi(self._client)
            self._relationships_api = api.TestCaseRelationshipServiceApi(self._client)

    @property
    def test_cases(self) -> List[TestCase]:
        """Retrieves all test cases in the test."""
        res = self._test_case_api.test_case_service_list_test_cases(self.key)
        if res and res.test_cases:
            return [TestCase._from_api_test_case(tc) for tc in res.test_cases]

        return []

    @property
    def test_case_relationships(self) -> List[TestCaseRelationship]:
        """Retrieves all relationships among test cases of the test."""
        r_a = self._relationships_api
        res = r_a.test_case_relationship_service_list_test_case_relationships(self.key)
        if res and res.test_case_relationships:
            return [
                TestCaseRelationship._from_api_test_case_rel(r)
                for r in res.test_case_relationships
            ]

        return []

    @property
    def documents(self) -> List[d7s.Document]:
        """Retrieves all documents attached to the test."""
        if not self._document_names:
            return []

        res = self._document_api.document_service_batch_get_documents(
            self._document_names
        )
        if res and res.documents:
            return [
                d7s.Document._from_api_document(d, self._client) for d in res.documents
            ]

        return []

    def perturb(
        self,
        new_test_name: str,
        perturbators: Union[p10s.Perturbator, str, List[Union[p10s.Perturbator, str]]],
        new_test_description: str = "",
    ) -> "Test":
        """Creates new Test by perturbing this test using the given perturbators.

        Args:
            new_test_name (str): Name of the newly created test.
            perturbators (Perturbator, List[Perturbator], str or List[str]): List of
                perturbators or their keys used to perturb this Test.
            new_test_description (str): Optional description of the newly created test.
        """

        if self._client is None:
            raise RuntimeError("Client is not set.")

        if not new_test_name:
            raise ValueError("New test name must be provided.")

        if not perturbators:
            raise ValueError("Perturbators must be provided.")

        if isinstance(perturbators, (p10s.Perturbator, str)):
            perturbators_to_run = [perturbators]
        else:
            perturbators_to_run = perturbators

        configs = [_PerturbatorConfiguration(p) for p in perturbators_to_run]

        req = models.TestServicePerturbTestRequest(
            perturbator_configurations=[c.to_api_proto() for c in configs],
            new_test_display_name=new_test_name,
            new_test_description=new_test_description,
        )
        resp = self._test_api.test_service_perturb_test(self.key, req)
        return Test._from_api_test(resp.test, self._client)

    def perturb_in_place(
        self,
        perturbators: Union[p10s.Perturbator, str, List[Union[p10s.Perturbator, str]]],
        test_case_names: Optional[List[str]] = None,
    ) -> str:
        """In-place (in-test) perturbation of test cases using the given perturbators.

        Args:
            perturbators (Perturbator, List[Perturbator], str or List[str]): List of
                perturbators or their keys used to perturb this Test.
            test_case_names (List[str]): List of test case names to perturb.
        """

        if self._client is None:
            raise RuntimeError("Client is not set.")

        if not perturbators:
            raise ValueError("Perturbators must be provided.")

        if isinstance(perturbators, (p10s.Perturbator, str)):
            perturbators_to_run = [perturbators]
        else:
            perturbators_to_run = perturbators

        configs = [_PerturbatorConfiguration(p) for p in perturbators_to_run]

        req = models.TestServicePerturbTestInPlaceRequest(
            perturbator_configurations=[c.to_api_proto() for c in configs],
            test_case_names=test_case_names,
        )
        resp = self._test_api.test_service_perturb_test(self.key, req)
        return resp.test.name

    def generate_test_cases(
        self,
        count: int,
        model: Optional[str] = None,
        base_llm_model: Optional[str] = None,
        generators: Optional[List[TestCaseGenerator]] = None,
        existing_collection: Optional[str] = None,
    ) -> None:
        """Generates test cases based on the documents of the Test.

        Args:
            count (int): Number of test cases to generate (generator may return fewer
                prompts).
            model (str): Model to use for generating the prompts.
            base_llm_model (str): Base LLM model to use for generating the prompts.
            generators (List[TestCaseGenerator]): Methods to use for generation.
            existing_collection (str): ID or the resource name of the existing
                collection, from which prompts will be generated.
                NOTE: This option works only for the H2OGPTe model host ATM.
        """

        req = models.TestServiceGenerateTestCasesRequest(
            count=count,
            model=model or None,
            base_llm_model=base_llm_model or None,
            generators=[g.to_api_proto() for g in generators] if generators else None,
            h2ogpte_collection_id=existing_collection or None,
        )

        res = self._test_api.test_service_generate_test_cases(self.key, req)

        op: models.V1Operation | None = res.operation
        self._gen_tc_op_name = op.name if op else None

    def wait_for_test_case_generation(
        self, timeout: Optional[float] = None, verbose: bool = False
    ) -> None:
        """Waits for the test case generation to finish.

        Args:
            timeout (float): The maximum time to wait in seconds.
            verbose (bool): If True, prints the status of the handle while waiting.
        """
        if not self._gen_tc_op_name:
            raise ValueError(
                "There is no ongoing test case generation - the operation name is not "
                "set."
            )

        if verbose:
            print(
                f"Waiting for test case generation to finish ({self._gen_tc_op_name}):"
            )
        if self._client:
            # exponential backoff
            wait_time = 1.0
            wait_coef = 1.6
            wait_max = 8.0
            wait_total = 0.0
            timeout = timeout or float(2 * 24 * 60 * 60)  # 2 days
            progress_bar = utils.ProgressBar()
            while wait_total < timeout:
                handle = _TestCaseGenerationHandle._from_operation(
                    self._operation_api.operation_service_get_operation(
                        self._gen_tc_op_name
                    )
                )

                if verbose:
                    progress_bar.update(handle.progress or 0, handle.progress_message)

                if handle.done:
                    if handle.error:
                        raise RuntimeError(
                            f"Test case generation failed: {handle.error}"
                        )
                    return

                wait_time *= wait_coef
                time.sleep(min(wait_time, wait_max))
        else:
            raise ValueError(
                "Unable to establish a connection to the Eval Studio host."
            )

        raise TimeoutError("Waiting timeout has been reached.")

    def list_test_suite_library_items(
        self,
        filter_by_categories: Optional[List[str]] = None,
        filter_by_purposes: Optional[List[str]] = None,
        filter_by_evaluates: Optional[List[str]] = None,
        filter_by_origin: Optional[str] = None,
        filter_by_test_case_count: Optional[int] = None,
        filter_by_test_count: Optional[int] = None,
        filter_by_fts: Optional[str] = None,
    ) -> List[TestCaseLibraryItem]:
        """Retrieves a list of all available items - suites of tests - in the library.

        Args:
            filter_by_categories (List[str]): List of categories to filter
                the library items.
            filter_by_purposes (List[str]): List of purposes to filter
                the library items.
            filter_by_evaluates (List[str]): List of evaluates to filter
                the library items.
            filter_by_origin (str): Origin to filter the library items.
            filter_by_test_case_count (int): Test case count to filter
                the library items.
            filter_by_test_count (int): Test count to filter the library items.
            filter_by_fts (str): FTS to filter the library items - phrase to search for.

        Returns:
            List[TestCaseLibraryItem]: List of library items.
        """
        req = models.TestServiceListTestCaseLibraryItemsRequest(
            filter_by_categories=filter_by_categories,
            filter_by_purposes=filter_by_purposes,
            filter_by_evaluates=filter_by_evaluates,
            filter_by_origin=filter_by_origin,
            filter_by_test_case_count=filter_by_test_case_count,
            filter_by_test_count=filter_by_test_count,
            filter_by_fts=filter_by_fts,
        )

        res = self._test_api.test_service_list_test_case_library_items(self.key, req)
        if res and res.prompt_library_items:
            return TestCaseLibraryItem._from_api_items(res.prompt_library_items)

        return []

    def add_library_test_cases(
        self, test_suite_url: str, count: int, test_document_urls: Optional[List[str]]
    ) -> None:
        """Sample test cases from the test suite library and add them to the test.

        Args:
            test_suite_url (str): The URL of the library test suite to get TestCases
                from (sample).
            count (int): The number of TestCases to get from the library.
            test_document_urls (List[str]): The list of target Test corpus
                document URLs to skip when returning library TestCases corpus.
        """
        req = models.TestServiceImportTestCasesFromLibraryRequest(
            test_suite_url=test_suite_url,
            count=count,
            test_document_urls=test_document_urls,
        )

        res = self._test_api.test_service_import_test_cases_from_library(self.key, req)

        op: models.V1Operation | None = res.operation
        self._lib_tc_op_name = op.name if op else None

    def wait_for_library_test_case_get(
        self, timeout: Optional[float] = None, verbose: bool = False
    ) -> None:
        """Waits for the library test cases(s) sampling  to finish.

        Args:
            timeout (float): The maximum time to wait in seconds.
            verbose (bool): If True, prints the status of the handle while waiting.
        """
        if not self._lib_tc_op_name:
            raise ValueError(
                "There is no ongoing getting of test case(s) from the library - "
                "the operation name is not set."
            )

        if verbose:
            print(
                f"Waiting for getting library test case(s) operation to finish "
                f"({self._lib_tc_op_name}):"
            )
        if self._client:
            # exponential backoff
            wait_time = 1.0
            wait_coef = 1.6
            wait_max = 8.0
            wait_total = 0.0
            timeout = timeout or float(2 * 24 * 60 * 60)  # 2 days
            progress_bar = utils.ProgressBar()
            while wait_total < timeout:
                handle = _TestCaseLibraryGetHandle._from_operation(
                    self._operation_api.operation_service_get_operation(
                        self._lib_tc_op_name
                    )
                )

                if verbose:
                    progress_bar.update(handle.progress or 0, handle.progress_message)

                if handle.done:
                    if handle.error:
                        raise RuntimeError(
                            f"Getting of library test case(s) failed: {handle.error}"
                        )
                    return

                wait_time *= wait_coef
                time.sleep(min(wait_time, wait_max))
        else:
            raise ValueError(
                "Unable to establish a connection to the Eval Studio host."
            )

        raise TimeoutError("Waiting timeout has been reached.")

    def delete(self, force=False):
        """Deletes the test.

        Args:
            force (bool): If True, test cases will be deleted as well.
        """
        self._test_api.test_service_delete_test(self.key, force=force)

    def create_test_case(
        self,
        prompt: str,
        answer: str,
        constraints: Optional[List[str]] = None,
        condition: str = "",
    ) -> Optional[TestCase]:
        """Creates a new test case in the test.

        Args:
            prompt (str): Prompt of the test case.
            answer (str): Expected answer of the test case.
            constraints (List[str]): String tokens expected in the actual answer.
                Note: all of the constraints in the list are concatenated using AND
                operator, which means actual answer need to contain all of the tokens.
            condition (str): Test case output condition, in a form logical expression.
                The format of the string is defined by the Google's filtering language.
                (ref. https://google.aip.dev/160#logical-operators)
        """
        case = TestCase(
            key="",
            prompt=prompt,
            answer=answer,
            constraints=constraints or [],
            condition=condition,
        )
        res = self._test_case_api.test_case_service_create_test_case(
            parent=self.key, test_case=case.to_api_proto()
        )
        if res and res.test_case:
            return TestCase._from_api_test_case(res.test_case)

        return None

    def remove_test_case(self, test_case_key: str):
        """Removes a test case from the test.

        Args:
            test_case_key (str): Resource name of the test case to be removed.
        """
        self._test_case_api.test_case_service_delete_test_case(test_case_key)

    def create_document(
        self, name: str, url: str, description: Optional[str] = None
    ) -> Optional[d7s.Document]:
        """Creates a new document and attaches it to the test.

        Args:
            name (str): Name of the document.
            url (str): URL of the document.
            description (str): Description of the document.
        """
        doc = d7s.Document("", name, description or "", url)
        res = self._document_api.document_service_create_document(doc.to_api_proto())
        if res and res.document:
            doc = d7s.Document._from_api_document(res.document, self._client)

        try:
            self.link_document(doc)
        except ValueError as err:
            raise RuntimeError("Failed to create the document.") from err
        except Exception as err:
            doc.delete()
            raise RuntimeError("Failed to link the document to the test.") from err

        return doc

    def link_document(self, document: d7s.Document):
        """Attaches an existing document to the test.

        Args:
            document (Document): Document to be attached to the test.
        """
        if not document.key:
            raise ValueError("Document must have a resource name.")

        self._document_names.append(document.key)
        try:
            self._test_api.test_service_update_test(
                test_name=self.key,
                test=models.RequiredTheTestToUpdate(documents=self._document_names),
            )
        except Exception as err:
            self._document_names.remove(document.key)
            raise RuntimeError("Failed to link the document to the test.") from err

    def unlink_document(self, document_key: str):
        """Deletes a document attached to the test.

        Args:
            document_key (str): Resource name of the document to be detached from the test.
        """
        try:
            self._document_names.remove(document_key)
        except ValueError as err:
            raise ValueError(
                f"Document {document_key} is not attached to the test."
            ) from err

        try:
            self._test_api.test_service_update_test(
                test_name=self.key,
                test=models.RequiredTheTestToUpdate(documents=self._document_names),
            )
        except Exception as err:
            self._document_names.append(document_key)
            raise RuntimeError("Failed to unlink the document from the test.") from err

    @staticmethod
    def _from_api_test(api_test: models.V1Test, client: api.ApiClient) -> "Test":
        return Test(
            key=api_test.name or "",
            name=api_test.display_name or "",
            description=api_test.description or "",
            create_time=api_test.create_time,
            update_time=api_test.update_time,
            _document_names=api_test.documents or [],
            _client=client,
        )


class _Tests:
    def __init__(self, client: api.ApiClient):
        self._client = client
        self._api = api.TestServiceApi(client)

    def list(self) -> List[Test]:
        """Retrieves all user tests in the Eval Studio."""
        res = self._api.test_service_list_tests()
        if res and res.tests:
            return [Test._from_api_test(t, self._client) for t in res.tests]

        return []

    def create(
        self,
        name: str,
        description: Optional[str] = "",
        documents: Optional[List[d7s.Document]] = None,
    ) -> Optional[Test]:
        """Creates a new test in the Eval Studio.

        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            documents (optional): List of `Document`s to be attached to the test.
        """
        _documents = [d.key for d in documents] if documents else None
        test = models.V1Test(
            display_name=name, description=description, documents=_documents
        )
        res = self._api.test_service_create_test(test)
        if res and res.test:
            return Test._from_api_test(res.test, self._client)

        return None

    def clone(
        self, key: str, name: Optional[str] = "", description: Optional[str] = ""
    ) -> Optional[Test]:
        """Clone an existing test in the Eval Studio.

        Args:
            key (str): Resource name of the test to be cloned.
            name (str): Optional new name of the cloned test.
            description (str): Optional new description of the cloned test.
        """
        res = self._api.test_service_clone_test(
            key,
            body=clone_test_request.TestServiceCloneTestRequest(
                new_test_display_name=name, new_test_description=description
            ),
        )

        if res and res.test:
            return Test._from_api_test(res.test, self._client)

        return None

    def delete(self, key: str):
        """Deletes the test with given resource name.

        Args:
            key (str): Resource name of the test to be deleted.
        """
        self._api.test_service_delete_test(key)

    def get(self, key: str) -> Test:
        """Get the test with given resource name.

        Args:
            key (str): Resource name of the test to be get.

        Returns:
            An instance of the retrieved `Test`.

        Raises:
            KeyError: If the test with the given key does not exist.
        """
        api_test = self._api.test_service_get_test(key)
        if not api_test or not api_test.test:
            raise KeyError(f"Test with key '{key}' does not exist.")

        return Test._from_api_test(api_test.test, self._client)

    def import_test_suite(
        self, test_suite: str, name_prefix: Optional[str] = None
    ) -> List[Test]:
        """Imports a list of tests (Test Suite) from a JSON.

        Args:
            test_suite (str): JSON string of the test suite.
            name_prefix (str): Optional prefix to name the imported tests.
        """
        req = models.V1BatchImportTestsRequest(
            testsJson=test_suite, testDisplayNamePrefix=name_prefix or None
        )
        res = self._api.test_service_batch_import_tests(req)
        if res and res.tests:
            return [Test._from_api_test(t, self._client) for t in res.tests]

        return []


class _PerturbatorConfiguration:
    """Represents the configuration of a perturbator to use during the perturbation process.

    Attributes:
        perturbator (Perturbator or str): Perturbator to use or its key.
    """

    def __init__(self, perturbator: Union[p10s.Perturbator, str]):
        self.name = (
            perturbator.key
            if isinstance(perturbator, p10s.Perturbator)
            else perturbator
        )
        self.intensity = (
            perturbator.intensity
            if isinstance(perturbator, p10s.Perturbator)
            else p10s.PerturbatorIntensity.medium
        )
        self.params = (
            perturbator.params if isinstance(perturbator, p10s.Perturbator) else None
        )

    def to_api_proto(self) -> models.V1PerturbatorConfiguration:
        """Converts the client PerturbatorConfiguration to an API PerturbatorConfiguration."""
        return models.V1PerturbatorConfiguration(
            name=self.name,
            intensity=self.intensity.to_api_proto(),
            params=json.dumps(self.params) if self.params else None,
        )
