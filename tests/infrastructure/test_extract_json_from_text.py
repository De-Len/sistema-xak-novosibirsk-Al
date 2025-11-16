from src.infrastructure.extract_json_from_text.extract_json_from_text import extract_json_from_text


def test_extract_valid_json():
    text = """
    Here is the data:
    ```json
    {"a": 1, "b": 2}
    ```
    """
    result = extract_json_from_text(text)
    assert result is not None
    assert '"a": 1' in result


def test_no_json_block():
    text = "No JSON inside"
    result = extract_json_from_text(text)
    assert result is None


def test_broken_json():
    text = """
    ```json
    {a:1,}
    ```
    """
    result = extract_json_from_text(text)
    assert result is None


def test_multiple_json_blocks_only_first_returned():
    text = """
    ```json
    {"a": 1}
    ```
    some text
    ```json
    {"b": 2}
    ```
    """
    result = extract_json_from_text(text)
    assert result.strip() == '{"a": 1}'