# chainsoup

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/thefcraft/chainsoup)
[![PyPI version](https://badge.fury.io/py/chainsoup.svg)](https://badge.fury.io/py/chainsoup)

**chainsoup** provides a fluent, pipeline-based interface for querying HTML and XML documents with BeautifulSoup, turning complex nested searches into clean, readable, and chainable method calls.

## The Problem

Working with [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) is great, but navigating deeply nested structures can lead to verbose and hard-to-read code:

```python
# Standard BeautifulSoup
try:
    doc = soup.find('div', class_='document')
    wrapper = doc.find('div', class_='documentwrapper')
    body_wrapper = wrapper.find('div', class_='bodywrapper')
    body = body_wrapper.find('div', class_='body')
    section = body.find('section', recursive=False)
    p_tag = section.find_all('p', recursive=False)[0]
    print(p_tag.text)
except AttributeError:
    print("One of the tags was not found.")

```

This pattern is repetitive, and the error handling can obscure the main logic.

## The Solution: A Fluent Pipeline

chainsoup elegantly solves this by introducing a `Pipeline` that lets you chain `find` operations. The same query becomes:

```python
from chainsoup import Pipeline

# With chainsoup
pipeline = Pipeline().find_tag('div', class_='document') \
                     .find_tag('div', class_='documentwrapper') \
                     .find_tag('div', class_='bodywrapper') \
                     .find_tag('div', class_='body') \
                     .find_tag('section', recursive=False) \
                     .find_all_tags('p', recursive=False)[0]

# Execute the pipeline and get the result
first_p = pipeline.raise_for_error.run(soup)
print(first_p.text)
```

or

```python 
from chainsoup import Pipeline, NestedArg, SpecalArg

# With chainsoup
pipeline = Pipeline().find_nested_tag(
    name = NestedArg() >> 'div' >> 'div' >> 'div' >> 'div' >> 'section',
    class_ = NestedArg() >> 'document' >> 'documentwrapper' >> 'bodywrapper' >> 'body',
    recursive = NestedArg() >> True >> True >> True >> True >> False >> SpecalArg.EXPANDLAST
).find_all_tags('p', recursive=False)[0]

# Execute the pipeline and get the result
first_p = pipeline.raise_for_error.run(soup)
print(first_p.text)
```

## Features

-   **Fluent Chaining:** Link `find_tag` and `find_all_tags` calls in a natural, readable sequence.
-   **Powerful Nested Searches:** Use `find_nested_tag` with `NestedArg` to perform complex deep searches with a single method call.
-   **Sequence Operations:** After a `find_all_tags` call, you can `filter`, `map`, and perform assertions on the sequence of results.
-   **Robust Error Handling:** Choose your style: either get a descriptive `Error` object back or have an exception raised automatically on failure.
-   **Intelligent Argument Resolution:** Automatically handle varying arguments for each level of a nested search.

## Installation

```bash
pip install chainsoup
```

## Quickstart

### 1. Basic Find

Create a `Pipeline` and chain `find_tag` calls to navigate to a specific element.

```python
from bs4 import BeautifulSoup
from chainsoup import Pipeline

html = '''
<body>
  <div id="content">
    <h1>Title</h1>
    <p>First paragraph.</p>
    <p>Second paragraph.</p>
  </div>
</body>
'''
soup = BeautifulSoup(html, 'html.parser')

# Build the pipeline
pipeline = Pipeline().find_tag('body').find_tag('div', id='content').find_tag('p')

# Execute it and raise an exception if any tag is not found
first_p = pipeline.raise_for_error.run(soup)
print(first_p.text)
# Output: First paragraph.

# Alternatively, execute without raising an error
result = pipeline.run(soup)
if not result:
    print(f"Pipeline failed: {result.msg}")
else:
    print(result.text)
```

### 2. Finding All Tags and Filtering

Use `find_all_tags` to get a sequence of results. This returns a `PipelineSequence` object, which you can use to filter, map, or select items.

```python
# Continues from the previous example...

# Find all <p> tags inside the div
p_sequence = Pipeline().find_tag('div', id='content').find_all_tags('p')

# Select the second paragraph (index 1)
second_p_pipeline = p_sequence[1]
print(second_p_pipeline.raise_for_error.run(soup).text)
# Output: Second paragraph.

# Or use .first / .last properties
first_p_pipeline = p_sequence.first
print(first_p_pipeline.raise_for_error.run(soup).text)
# Output: First paragraph.

# Filter the sequence
contains_second = lambda tag: "Second" in tag.text
filtered_sequence = p_sequence.filter(contains_second)

# This will now find the first (and only) tag that matches the filter
result = filtered_sequence.first.raise_for_error.run(soup)
print(result.text)
# Output: Second paragraph.
```

## Advanced Usage: `find_nested_tag`

The `find_nested_tag` method is the most powerful feature of chainsoup. It allows you to define an entire path of `find` operations in a single, declarative call using `NestedArg`.

### `NestedArg`

An `NestedArg` is a fluent builder for creating a list of arguments, one for each level of the search. You can chain values using the `>>` operator or the `.add()` method.

### Example

Let's revisit the complex example from the introduction.

```python
from chainsoup import Pipeline, NestedArg, SpecalArg

# ... setup soup ...

pipeline = Pipeline().find_nested_tag(
    # For each level of the search, specify the tag 'name'
    name = NestedArg() >> 'body' >> 'div' >> 'div' >> 'div' >> 'div',

    # Specify attributes for each level. The lists are matched by index.
    attrs={
        'class': NestedArg() >> None >> 'document' >> 'documentwrapper' >> 'bodywrapper' >> 'body'
    },
    
    # Specify the `recursive` flag. Here, we use a Special Argument.
    # It will be True, then False, and EXPANDLAST will repeat `False` for the rest.
    recursive = NestedArg() >> True >> False >> SpecalArg.EXPANDLAST

).find_all_tags(
    name='section',
    recursive=False
).first.find_all_tags(
    name='p',
    recursive=False
)

# Create two branches of the pipeline to get the first and second <p> tags
first_p_pipeline = pipeline[0]
second_p_pipeline = pipeline[1]

# Execute both
print(first_p_pipeline.raise_for_error.run(soup).text)
print(second_p_pipeline.raise_for_error.run(soup).text)
```

### `SpecalArg` Enum

When argument lists have different lengths, `SpecalArg` controls how the shorter lists are padded to match the longest one.

-   `SpecalArg.EXPANDLAST`: Repeats the last provided value.
-   `SpecalArg.FILLNONE`: Fills with `None` (the default).
-   `SpecalArg.FILLTRUE`: Fills with `True`.
-   `SpecalArg.FILLFALSE`: Fills with `False`.

## API Overview

-   **`Pipeline`**: The main object for building a query that results in a **single `Tag`**.
    -   `.find_tag(...)`: Appends a `find` operation.
    -   `.find_nested_tag(...)`: Appends a series of `find` operations.
    -   `.find_all_tags(...)`: Transitions the query into a `PipelineSequence`.
    -   `.run(soup)`: Executes the pipeline and returns a `Tag` or `Error` object.
    -   `.run_and_raise_for_error(soup)`: Executes and raises an `Error` on failure.

-   **`PipelineSequence`**: An object for building a query that results in a **sequence of `Tag`s**.
    -   `.filter(fn)`: Filters the sequence.
    -   `.map(fn)`: Applies a function to each tag in the sequence.
    -   `.assert_all(fn)`: Asserts a condition for all tags.
    -   `.first`, `.last`, `[index]`: Selects a single element, returning control to a `Pipeline`.

-   **`NestedArg`**: A helper class to build argument lists for `find_nested_tag`.

## Contributing

Contributions are welcome! If you have a feature request, find a bug, or want to improve the documentation, please open an issue or submit a pull request on our [GitHub repository](https://github.com/your-username/chainsoup).

## License

This project is licensed under the MIT License.