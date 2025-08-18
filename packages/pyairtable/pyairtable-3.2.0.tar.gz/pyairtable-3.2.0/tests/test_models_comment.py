import datetime

import pytest

from pyairtable.models import Comment
from pyairtable.testing import fake_id, fake_user

RECORD_ID = "recHasSomeComments"
NOW = datetime.datetime.now().isoformat()


@pytest.fixture
def comment_json(sample_json):
    return sample_json("Comment")


@pytest.fixture
def comment(comment_json, table):
    record_url = table.urls.record(RECORD_ID)
    return Comment.from_api(comment_json, table.api, context={"record_url": record_url})


@pytest.fixture
def comments_url(base, table):
    return f"https://api.airtable.com/v0/{base.id}/{table.name}/{RECORD_ID}/comments"


def test_parse(comment):
    assert isinstance(comment.created_time, datetime.datetime)
    assert isinstance(comment.last_updated_time, datetime.datetime)
    assert comment.author.id == "usrLkNDICXNqxSDhG"
    assert comment.mentioned["usr00000mentioned"].display_name == "Alice Doe"
    assert comment.reactions[0].emoji == "👍"


def test_missing_attributes(comment_json):
    """
    Test that we can parse the payload when missing optional values.
    """
    del comment_json["lastUpdatedTime"]
    del comment_json["mentioned"]
    comment = Comment.model_validate(comment_json)
    assert comment.mentioned == {}
    assert comment.last_updated_time is None


@pytest.mark.parametrize(
    "attr,value",
    [
        ("id", fake_id("rec", "FAKE")),
        ("created_time", "2023-06-07T17:35:17"),
        ("last_updated_time", "2023-06-07T17:35:17"),
        ("mentioned", {}),
        ("author", {}),
    ],
)
def test_readonly_attributes(comment, attr, value):
    """
    Test that we cannot modify any attributes on a Comment besides ``text``.
    """
    with pytest.raises(AttributeError):
        setattr(comment, attr, value)


def test_save(comment, requests_mock):
    """
    Test that Comment.save() writes the correct payload to the API
    and that it updates the instance with the values in the API response.
    """
    new_text = "This was changed!"
    mentions = {}
    modified = dict(comment._raw, mentioned=mentions, text=new_text)
    m = requests_mock.patch(comment._url, json=modified)

    comment.text = "Whatever"
    comment.save()
    assert m.call_count == 1

    # Ensure we wrote the changed text to the API...
    assert m.request_history[0].json()["text"] == "Whatever"

    # ...but our model loaded whatever values the API sent back.
    assert comment.text == new_text
    assert comment.author.email == "author@example.com"
    assert not comment.mentioned


def test_delete(comment, requests_mock):
    """
    Test that Comment.delete() writes the correct payload to the API
    and prevents the record from being saved in the future.
    """
    m = requests_mock.delete(comment._url, json={"id": comment.id, "deleted": True})
    comment.delete()
    assert m.call_count == 1
    assert comment.deleted is True

    # Once we have deleted a comment, we shouldn't be allowed to save it.
    with pytest.raises(RuntimeError):
        comment.save()


# TODO: test_table_comments should probably be in test_api_table.py
def test_table_comments(table, comments_url, comment_json, requests_mock):
    """
    Test that Table.comments() returns a list of comments and that
    it requests all pages at once.
    """
    comment1 = {**comment_json, "id": "comFake1"}
    comment2 = {**comment_json, "id": "comFake2"}
    comment3 = {**comment_json, "id": "comFake3"}

    m = requests_mock.get(
        comments_url,
        [
            {"json": {"comments": [comment1], "offset": "offset1"}},
            {"json": {"comments": [comment2, comment3], "offset": None}},
        ],
    )

    comments = table.comments(RECORD_ID)
    assert m.call_count == 2
    assert len(comments) == 3
    assert [c.id for c in comments] == ["comFake1", "comFake2", "comFake3"]
    assert fake_user("mentioned")["id"] in comments[0].mentioned


# TODO: test_table_comment should probably be in test_api_table.py
def test_table_add_comment(table, comment_json, comments_url, requests_mock):
    def _callback(request, context):
        return {**comment_json, **request.json()}

    m = requests_mock.post(comments_url, json=_callback)

    text = "I'd like to weigh in here."
    comment = table.add_comment(RECORD_ID, text)
    assert m.call_count == 1
    assert comment.text == text
