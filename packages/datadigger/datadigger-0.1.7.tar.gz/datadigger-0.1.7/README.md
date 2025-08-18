# datadigger

`datadigger` is a Python package designed to simplify text processing tasks, such as extracting, manipulating, and saving text data from various sources. It includes utility functions for working with text, handling files (e.g., reading/writing CSV), interacting with HTML elements via BeautifulSoup, and performing operations like string standardization, element extraction with CSS selectors, and more. 

Key features include:
- String manipulation and sanitization.
- CSV file handling with optional appending or header control.
- HTML parsing using BeautifulSoup to extract text or attributes via CSS selectors and from json objects.
- Flexible error handling for missing or invalid inputs. 


## Installation

You can install this package via pip:

```bash
pip install datadigger

# ================================================================

from datadigger import create_directory
# Creates a directory if it doesn't already exist.


# Example 1: Creating a new directory
create_directory("new_folder")

# Example 2: Creating nested directories
create_directory("parent_folder/sub_folder")

# ================================================================

from datadigger import standardized_string
# This function standardizes the input string by removing escape sequences like \n, \t, and \r, removing HTML tags, collapsing multiple spaces, and trimming leading/trailing spaces.


# Example 1: Standardize a string with newlines, tabs, and HTML tags
input_string_1 = "<html><body>  Hello \nWorld!  \tThis is a test.  </body></html>"
print("Standardized String 1:", standardized_string(input_string_1))

# Example 2: Input string with multiple spaces and line breaks
input_string_2 = "  This   is   a  \n\n   string   with  spaces and \t tabs.  "
print("Standardized String 2:", standardized_string(input_string_2))

# Example 3: Pass an empty string
input_string_3 = ""
print("Standardized String 3:", standardized_string(input_string_3))

# Example 4: Pass None (invalid input)
input_string_4 = None
print("Standardized String 4:", standardized_string(input_string_4))

================================================================

from datadigger import remove_common_elements
# The function removes elements from the remove_in collection that are present in the remove_by collection.


# Example 1: Removing common elements between two lists
remove_in = [1, 2, 3, 4, 5]
remove_by = [3, 4, 6]
result = remove_common_elements(remove_in, remove_by)
print(result)  # Output: [1, 2, 5]

# Example 2: Removing common elements between a set and a tuple
remove_in = {1, 2, 3, 4, 5}
remove_by = (3, 4, 6)
result = remove_common_elements(remove_in, remove_by)
print(result)  # Output: {1, 2, 5}

# Example 3: Missing one argument (should print an error message)
result = remove_common_elements(remove_in, None)  # Output: "Value not passed for: remove_by"

# Example 4: Missing both arguments (should print an error message)
result = remove_common_elements(None, None)  # Output: "Value not passed for: remove_in, remove_by"

================================================================

from datadigger import save_to_csv
# The save_to_csv function saves data to a CSV file, appending to an existing file or creating a new one, and includes optional column headers and a customizable delimiter.

# Example data to be saved
list_data = [[1, 'Alice', 23], [2, 'Bob', 30], [3, 'Charlie', 25]]
column_header_list = ['ID', 'Name', 'Age']
output_file_path = 'output_data.csv'

# Save with the default separator (comma)
save_to_csv(list_data, column_header_list, output_file_path)

# Save with a tab separator
save_to_csv(list_data, column_header_list, output_file_path, sep="\t")

# Save with a semicolon separator
save_to_csv(list_data, column_header_list, output_file_path, sep=";")

# Sample Output

# If sep="," (default), the CSV file will look like this:

ID,Name,Age
1,Alice,23
2,Bob,30
3,Charlie,25

# If sep="\t" (tab), the CSV file will look like this: 

ID	Name	Age
1	Alice	23
2	Bob	30
3	Charlie	25

================================================================

from datadigger import read_csv
# The read_csv function reads a CSV file into a Pandas DataFrame, with optional filtering and column value extraction based on specified criteria.

# Example 1: Read from a CSV file with the default separator (comma)

csv_file_path = 'data.csv'
get_value_by_col_name = 'URL'
filter_col_name = 'Category'
inculde_filter_col_values = ['Tech']

result = read_csv(csv_file_path, get_value_by_col_name, filter_col_name, inculde_filter_col_values)
print(result)

# Sample Output

Category,URL
Tech,https://tech1.com
Tech,https://tech2.com
Science,https://science1.com

# Example 2: Read from a CSV file with a custom separator (tab)

result = read_csv(csv_file_path, get_value_by_col_name, filter_col_name, inculde_filter_col_values, sep="\t")
print(result)

# Sample Output

Category	URL
Tech	https://tech1.com
Tech	https://tech2.com
Science	https://science1.com

================================================================

from datadigger import get_json_content
# The function returns the standardized value (using standardized_string()) if it’s a basic data type like str, int, or float. Otherwise, it returns the raw JSON object or an empty string if nothing is found.

json_data = {"user": {"name": "John", "age": 30}}
keys = ["user", "name"]
result = get_json_content(json_data, keys)
print(result)  # Output: "John"

================================================================

from bs4 import BeautifulSoup
from datadigger import get_selector_content
# The get_selector_content function extracts text or attribute values from a BeautifulSoup-parsed HTML document using CSS selectors, with options for specific element matching, attribute retrieval, or full text extraction.


html_content = """
<html>
  <body>
    <div class="example">Example Text</div>
    <a href="https://example.com">Link</a>
  </body>
</html>
"""
soup = BeautifulSoup(html_content, "html.parser")

# Extract all elements matching a selector
print(get_selector_content(soup, css_selector_ele=".example"))

# Extract the text of the first matching element
print(get_selector_content(soup, css_selector=".example"))

# Extract the 'href' attribute of the first matching element
print(get_selector_content(soup, css_selector="a", attr="href"))

# Extract the entire text content of the soup object
print(get_selector_content(soup))

# Sample Output

[<div class="example">Example Text</div>]
Example Text
https://example.com
Example Text Link

================================================================

from datadigger import get_xpath_content
from lxml import etree


# Example tree (we'll parse the HTML string into a tree)
html_content = """
<html>
    <body>
        <div>
            <h1>Welcome to My Website</h1>
            <p class="description">This is a paragraph with some text.</p>
            <a href="http://example.com" id="example-link">Click here</a>
        </div>
    </body>
</html>
"""

# Parsing the HTML content
tree = etree.HTML(html_content)

# XPath to extract the text content of the <h1> tag
h1_content = get_xpath_content(tree, xpath="//h1")
print(h1_content)  # Output: "Welcome to My Website"

# XPath to extract the href attribute from the <a> tag
href = get_xpath_content(tree, xpath="//a[@id='example-link']", attr="href")
print(href)  # Output: "http://example.com"

# XPath to extract the id attribute from the <a> tag
link_id = get_xpath_content(tree, xpath="//a", attr="id")
print(link_id)  # Output: "example-link"

================================================================

from datadigger import save_file

save_file("output", "This is a new file.", "example.txt")  # Default write mode and UTF-8 encoding
save_file("output", "Appending content.", "example.txt", mode="a")  # Append mode
save_file("output", "Special characters: äöüß", "example_latin1.txt", encoding="latin-1")  # Custom encoding

================================================================

from datadigger import read_file

# Reading the file
content = read_file("output/example.txt")
print(content)

