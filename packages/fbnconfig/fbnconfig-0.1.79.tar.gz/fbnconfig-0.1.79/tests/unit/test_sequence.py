import json
from types import SimpleNamespace

import httpx
import pytest

from fbnconfig import sequence

TEST_BASE = "https://foo.lusid.com"


def response_hook(response: httpx.Response):
    response.read()
    response.raise_for_status()


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeSequenceResource:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    def test_create(self, respx_mock):
        respx_mock.post("/api/api/sequences/scope-a").mock(return_value=httpx.Response(200, json={}))
        # given a desired sequence where we default the startValue
        sut = sequence.SequenceResource(
            id="xyz",
            scope="scope-a",
            code="code-a",
            increment=2,
            min_value=1,
            max_value=100,
            pattern="SQP-{{seqValue}}",
        )
        # when we create it
        state = sut.create(self.client)
        # then the state is returned
        assert state == {"scope": "scope-a", "code": "code-a"}
        # and a create request was sent without the startValue
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/api/api/sequences/scope-a"
        assert json.loads(request.content) == {
            "scope": "scope-a",
            "code": "code-a",
            "increment": 2,
            "minValue": 1,
            "maxValue": 100,
            "pattern": "SQP-{{seqValue}}",
        }

    def test_update_with_no_changes(self, respx_mock):
        # given an existing sequence
        respx_mock.get("/api/api/sequences/scope-a/code-a").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": {"scope": "scope-a", "code": "code-a"},
                    "increment": 2,
                    "startValue": 1,
                    "minValue": 1,
                    "maxValue": 100,
                    "pattern": "SQP-{{seqValue}}",
                },
            )
        )
        # and a desired with increment but everything else defaulted
        sut = sequence.SequenceResource(id="seq2", scope="scope-a", code="code-a", increment=2)
        old_state = SimpleNamespace(scope="scope-a", code="code-a")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the state is None
        assert state is None
        # and a read was made but no PUT

    def test_update_with_changes_throws(self, respx_mock):
        # given an existing sequence
        respx_mock.get("/api/api/sequences/scope-a/code-a").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": {"scope": "scope-b", "code": "code-b"},
                    "scope": "scope-a",
                    "code": "code-a",
                    "increment": 2,
                    "startValue": 1,
                    "minValue": 1,
                    "maxValue": 100,
                    "pattern": "SQP-{{seqValue}}",
                },
            )
        )
        # and a desired with a different increment
        sut = sequence.SequenceResource(id="seq2", scope="scope-a", code="code-a", increment=200)
        old_state = SimpleNamespace(scope="scope-a", code="code-a")
        # when we update it throws
        with pytest.raises(RuntimeError):
            sut.update(self.client, old_state)

    def test_delete_throws(self):
        # given a resource that exists in the remnte
        old_state = SimpleNamespace(scope="scope-b", code="code-b")
        # when we delete it throws
        with pytest.raises(RuntimeError):
            sequence.SequenceResource.delete(self.client, old_state)

    def test_deps(self):
        sut = sequence.SequenceResource(id="xyz", scope="scope-b", code="code-b")
        # it's deps are empty
        assert sut.deps() == []
