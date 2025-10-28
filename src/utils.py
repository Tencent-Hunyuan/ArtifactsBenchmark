import os
import time
import json
from pathlib import Path
from code_parser import extract_html
from extract_ans import extract_last_html_or_svg_block
from playwright.sync_api import sync_playwright


def get_query(line_data):
    """
    Retrieves the query from the given line data by checking various possible fields.

    Parameters:
    - line_data: Dictionary containing information about the line.

    Returns:
    - str: The query string retrieved from the available fields (or an empty string if no query is found).
    """
    return (
        line_data.get("original_question")
        or line_data.get("question")
        or line_data.get("input")
        or line_data.get("prompt")
        or ""
    )


def get_answer(line_data):
    """
    Retrieves the answer from the given line data by checking various possible fields.

    Parameters:
    - line_data: Dictionary containing information about the line.

    Returns:
    - str: The answer string retrieved from the available fields, trimmed of unnecessary tags.
    """
    answer = (
        line_data.get("model_infer_result")
        or line_data.get("output")
        or line_data.get("answer")
        or ""
    )
    return answer.split("</think>")[-1].strip()


def extract_html_or_svg(answer):
    """
    Extracts the HTML or SVG block from the answer.

    Parameters:
    - answer: The answer string to extract HTML or SVG from.

    Returns:
    - dict: A dictionary with "type" (either "html" or "svg") and "content" (the extracted content).
            Returns None if neither HTML nor SVG is found.
    """
    extracted = extract_last_html_or_svg_block(answer)
    if extracted["type"] not in ("html", "svg"):
        return None
    return extracted


def extract_html_content(answer, extracted):
    """
    Extracts HTML content from the answer, with a fallback to the extracted content if an error occurs.

    Parameters:
    - answer: The answer string to extract HTML from.
    - extracted: The extracted HTML/SVG block.

    Returns:
    - str: The extracted HTML content, or the raw extracted content if an error occurs.
    """
    if extracted['type'] == 'html':
        try:
            html_code = extract_html(answer)
        except:
            html_code = extracted['content']
    else:
        html_code = extracted['content']
    return html_code


def extract_information(index, line_data, count, screenshots_dir):
    """
    Extracts the relevant information (query, answer, HTML/SVG content) from the given line_data,
    and generates screenshots of the extracted content.

    Parameters:
    - index: The index of the current item in the dataset.
    - line_data: Dictionary containing the item data.
    - count: The number of screenshots to capture.
    - screenshots_dir: Directory to store the screenshots.

    Returns:
    - tuple: A tuple containing the list of image paths, the query, and the answer.
            Returns None for the image paths if there is no valid answer or content.
    """
    try:
        query = get_query(line_data)
        answer = get_answer(line_data)

        if not answer:
            print(f"[Warning] index={index}: No valid answer found!")
            return None, query, answer

        extracted = extract_html_or_svg(answer)
        if not extracted:
            return None, query, answer

        html_path = os.path.join(screenshots_dir, f"html_{index}.html")
        html_code = extract_html_content(answer, extracted)

        # Save HTML content to a file
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_code)

        # Generate file paths for the screenshots
        img_path = [
            os.path.join(screenshots_dir, f"screenshot_{index}_{i + 1}.png")
            for i in range(count)
        ]
        capture_html_screenshots(html_path, img_path, count)

        return img_path, query, answer
    except Exception as e:
        print(f"[Error] index={index}: {str(e)}")
        return None, query, answer


def capture_html_screenshots(
    html_path, img_path, num_screenshots=3, interval=1, max_retries=2, timeout=600000
):
    """
    Captures screenshots of the given HTML content using Playwright.

    Parameters:
    - html_path: Path to the HTML file to capture screenshots from.
    - img_path: List of file paths where the screenshots will be saved.
    - num_screenshots: The number of screenshots to capture (default is 3).
    - interval: Time interval between screenshots (default is 1 second).
    - max_retries: Maximum number of retry attempts in case of failure (default is 2).
    - timeout: Timeout duration for the page loading and screenshot capture (default is 600000 milliseconds).

    Returns:
    - None: This function doesn't return anything but captures screenshots at the specified paths.
    """
    try:
        html_path = Path(html_path) if not isinstance(
            html_path, Path) else html_path
        for attempt in range(1, max_retries + 1):
            try:
                # Launch the browser using Playwright
                with sync_playwright() as pw:
                    browser = pw.chromium.launch(headless=True)
                    try:
                        context = browser.new_context()
                        page = context.new_page()
                        page.set_default_timeout(timeout)
                        page.goto(
                            f"file://{html_path.resolve()}", timeout=timeout)
                        page.wait_for_load_state(
                            "networkidle", timeout=timeout)

                        # Capture screenshots
                        for i in range(num_screenshots):
                            page.screenshot(
                                path=img_path[i], full_page=True, timeout=timeout
                            )
                            if i < num_screenshots - 1:
                                time.sleep(interval)
                        break  # Exit after successful screenshot capture
                    finally:
                        if context:
                            context.close()
                        if browser:
                            browser.close()
            except Exception as e:
                if attempt == max_retries:
                    print(f"Attempt {attempt} failed, Error: {str(e)}")
                    return None
                else:
                    print(
                        f"Attempt {attempt} failed, retrying... Error: {
                            str(e)}")
    finally:
        pass


def truncate_content(text, tokenizer, max_tokens=27000):
    """
    Truncates the given text to fit within the specified token limit.

    Parameters:
    - text: The text to truncate.
    - tokenizer: The tokenizer used to encode the text.
    - max_tokens: The maximum allowed token count (default is 27000 tokens).

    Returns:
    - str: The truncated text.
    """
    tokens = tokenizer.encode(text)
    if len(tokens) > max_tokens:
        text = tokenizer.decode(tokens[:max_tokens])
    return text


def load_data_from_file(file_path):
    """
    Loads data from a JSON file, one line at a time.

    Parameters:
    - file_path: Path to the JSON file containing the data.

    Returns:
    - list: A list of dictionaries containing the loaded data.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        all_data = [json.loads(line) for line in f]
    return all_data
