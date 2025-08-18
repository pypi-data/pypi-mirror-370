# datadigger/utils.py
import csv
import json
import os
import re
from typing import Union, Optional, List, Dict, Any

import urllib.parse
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree
from ftfy import fix_text


def create_directory(directory_name: str) -> None:
    """
    Creates a directory if it doesn't already exist.

    Args:
    - directory_name (str): The name of the directory to create.

    Returns:
    - None
    """
    try:
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
    except OSError as error:
        # print(f"Error: {error}")
        pass



def standardized_string(string: str = None) -> str:
    """
    Standardizes a string by:
    - Replacing `\n`, `\t`, and `\r` with spaces.
    - Removing HTML tags.
    - Replacing multiple spaces with a single space.
    - Stripping leading/trailing spaces.

    Args:
    - string (str, optional): The string to be standardized. Defaults to None.

    Returns:
    - str: The standardized string, or an empty string if input is None.
    """
    if string is None:
        return ""
    # Fix encoding issues (mojibake)
    string = fix_text(string)

    string = string.replace("\\n", " ").replace("\\t", " ").replace("\\r", " ")
    string = re.sub(r"<.*?>", " ", string)  # Remove HTML tags
    string = re.sub(r"\s+", " ", string)  # Collapse multiple spaces into one
    string = string.strip()  # Strip leading/trailing spaces
    return string


def get_keys(data: List[Dict]) -> List[str]:
    """
    This function takes a list of dictionaries as input and returns the keys of the first dictionary
    in the list if it exists.

    Parameters:
    data (List[Dict]): A list containing dictionaries, where each dictionary represents an event or object.

    Returns:
    List[str]: A list of keys from the first dictionary in the list.
    """
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        return list(data[0].keys())
    elif isinstance(data, dict) and len(data) > 0:
        return list(data.keys())
    else:
        return []


def get_html_object(page_source: Optional[str] = None, soup_obj: Optional[bool] = None,
                    lxml_tree_obj: Optional[bool] = None) -> Any:
    """
    Parse the page source into either a BeautifulSoup object or an lxml Element.

    Parameters:
    - page_source: The raw HTML or XML string to be parsed.
    - soup_obj: A flag to determine if BeautifulSoup should be used.
    - lxml_tree_obj: A flag to determine if lxml should be used.

    Returns:
    - A BeautifulSoup object (if soup_obj is True).
    - An lxml Element (if lxml_tree_obj is True).
    - An empty string in case of errors or missing data.
    """
    if soup_obj:
        try:
            # Parse using BeautifulSoup
            return BeautifulSoup(page_source, "html.parser")
        except Exception as e:
            print(f"Error in BeautifulSoup parsing: {e}")
            return ""  # Return empty string in case of failure

    elif lxml_tree_obj:
        try:
            # Attempt to convert tree to an lxml Element using etree.HTML or etree.fromstring
            return etree.HTML(page_source) if isinstance(page_source, str) else etree.fromstring(page_source)
        except (ValueError, etree.XMLSyntaxError) as e:
            print(f"Error in lxml parsing: {e}")
            return ""  # Return empty string in case of failure

    return ""  # Default return if neither soup_obj nor lxml_tree_obj is provided


def extract_json_string_from_patterns(script_content: str = None, patterns: Optional[list] = None) -> Optional[str]:
        """
        Extracts a JSON string from the script content using a list of regex patterns.

        Args:
            script_content (str): The content of the script tag.
            patterns (Optional[list]): A list of regex patterns to search for. Defaults to None.
        
        Returns:
            Optional[str]: The matched JSON string if found; None if no matching JSON is found.
        """
        # Default regex patterns to search for specific window variables
        default_patterns = [
            rf'{re.escape("window.__INITIAL_STATE__")}\s*=\s*(\{{.*\}});',
            rf'{re.escape("window.__SERVER_DATA__")}\s*=\s*(\{{.*\}});',
            rf'{re.escape("window.SERVER_PRELOADED_STATE_DETAILS")}\s*=\s*(\{{.*\}});'
        ]
        
        # Joine patterns and default 
        patterns = (patterns or []) + default_patterns

        # Compile the regex patterns for efficiency if not already compiled
        compiled_patterns = [re.compile(pattern) for pattern in patterns]

        for pattern in compiled_patterns:
            try:
                # Search for the pattern in the script content
                json_match = pattern.search(script_content)
                
                if json_match:
                    # Return the matched JSON string directly without parsing
                    return json_match.group(1)
            except re.error as e:
                # Log or print the regex compilation error for debugging
                print(f"Regex error: {e}")
                continue
        
        return None  # Return None if no JSON string was found

def get_json_by_keyword(soup_obj: BeautifulSoup = None, find_by_tag_name: str = None, search_keyword: str = None) -> \
Optional[Dict[str, Any]]:
    """
    Extracts a JSON object from a <script> tag containing the specified keyword.

    Args:
        html_content (str): The HTML content to parse.
        keyword (str, optional): The unique identifier to locate the script tag.
                                 Defaults to "window.SERVER_PRELOADED_STATE_DETAILS".

    Returns:
        Optional[Dict[str, Any]]: The parsed JSON object as a dictionary if found;
                                  None if no matching script tag or JSON object is found.
    """
    # Parse the HTML with BeautifulSoup
    preset_keywords = ['window.__INITIAL_STATE__', 'window.__SERVER_DATA__','window.SERVER_PRELOADED_STATE_DETAILS']

    if soup_obj is None:
        return None

    # Find the script tag containing the desired keyword in its content
     # Find the script tag
    try:
        if search_keyword is None:
            script_tag = next(
                (script for script in soup_obj.find_all(find_by_tag_name)
                 if script.string and any(keyword in script.string for keyword in preset_keywords)),
                None
            )
            if script_tag:
                search_keyword = next(
                    (keyword for keyword in preset_keywords if keyword in script_tag.string),
                    None
                )
        else:
            script_tag = next(
                (script for script in soup_obj.find_all(find_by_tag_name)
                 if script.string and search_keyword in script.string),
                None
            )

        if not script_tag or not script_tag.string:
                return None            

        # Extract the text from the script tag
        script_content = script_tag.string
    
        # Parse and return the JSON object
        try:
            # Locate the JSON object within the script content
            json_start = script_content.find("{")
            json_end = script_content.rfind("}") + 1  # Include the closing brace
            json_string = script_content[json_start:json_end]
            return json.loads(json_string.strip(), strict=False)
        except:
            # Dynamically create a regex pattern based on the keyword
            pattern = rf'{re.escape(search_keyword)}\s*=\s*(\{{.*?\}});' if search_keyword else None
            json_string = extract_json_string_from_patterns(script_content = json_string, patterns = [pattern])
            try:
                return json.loads(json_string.strip(), strict=False)
            except Exception as e:
                print(e)
    except Exception as error:
        return error

def get_json_by_ld_json(soup_obj: BeautifulSoup = None, find_by_css_selector: Optional[str] = None) -> Any:
    ld_json_list = list()
    if soup_obj is None:
        return None

    for ld_json_data in soup_obj.select(find_by_css_selector):
        if ld_json_data:
            try:
                ld_json_text = ld_json_data.text
                ld_json_text = ld_json_text.replace("\\n", " ").replace("\\t", " ").replace("\\r", " ")
                ld_json_text = re.sub(r"\s+", " ", ld_json_text)
                ld_json = json.loads(ld_json_text.strip(), strict=False)
                ld_json_list.append(ld_json)
            except Exception as error:
                return ""
    return ld_json_list


def get_json_obj(page_source: Optional[str] = None, ld_json_type: bool = True,
             find_by_css_selector: str = '[type="application/ld+json"]', find_by_tag_name: str = 'script',
             search_keyword: str = None) -> Any:
    if page_source is None:
        return None

    # If pagse source is not a soup object, try to convert it
    if not isinstance(page_source, BeautifulSoup):
        page_source = get_html_object(page_source=page_source, soup_obj=True)

    if ld_json_type is False:
        return get_json_by_keyword(soup_obj=page_source, find_by_tag_name=find_by_tag_name,
                                   search_keyword=search_keyword)
    return get_json_by_ld_json(soup_obj=page_source, find_by_css_selector=find_by_css_selector)


def process_json_list_to_dict(json_obj: list = None) -> Union[list, dict, None]:
    if isinstance(json_obj, list):
        for json_obj_value in json_obj:
            if isinstance(json_obj_value, dict):
                return json_obj_value
    else:
        return json_obj


def get_json_first_key_content(json_obj: Union[list, dict] = None, keys: list = None) -> Any:
    """
    purpose of searching a nested structure for a key.
    Focuses on extracting the first match.
    """

    if json_obj is None or keys is None:
        return None

    def find_key_value(dict_data, key):
        if isinstance(dict_data, dict):
            if key in dict_data:
                return dict_data[key], True
            for v in dict_data.values():
                result, found = find_key_value(v, key)
                if found:
                    return result, True
        elif isinstance(dict_data, list):
            for item in dict_data:
                result, found = find_key_value(item, key)
                if found:
                    return result, True
        return "", False

    result_dict = {}
    for key in keys:
        value, found = find_key_value(dict_data=json_obj, key=key)
        result_dict[key] = value

    return result_dict


def get_json_last_key_content(json_obj: Union[list, dict] = None, keys: list = None) -> Any:
    """
    Focuses on extracting the last match.
    """
    if json_obj is None or keys is None:
        return None

    for key in keys:
        if isinstance(json_obj, dict):
            if key in json_obj:
                json_obj = json_obj[key]
            else:
                # return (False, None)
                return ""
        elif isinstance(json_obj, list):
            found = False
            for item in json_obj:
                if isinstance(item, dict) and key in item:
                    json_obj = item[key]
                    found = True
                    break
            if not found:
                # return (False, None)
                return ""
        else:
            # return (False, None)
            return ""
    # return (True, json_obj)
    return standardized_string(json_obj) if isinstance(json_obj, (int, float, str)) else json_obj if json_obj else ""


def get_json_content(json_obj: Union[list, dict] = None, keys: list = None, value_type: str = "first") -> Any:
    if json_obj is None or keys is None:
        return None

    if value_type == "first":
        return get_json_first_key_content(json_obj=json_obj, keys=keys)
    elif value_type == "last" and value_type:
        return get_json_last_key_content(json_obj=json_obj, keys=keys)
    else:
        return None


def get_selector_content(soup_obj: Optional[BeautifulSoup], css_selector_ele: Optional[str] = None,
                         css_selector: Optional[str] = None, attr: Optional[str] = None) -> Any:
    """
    Extracts content from a BeautifulSoup object based on CSS selectors and attributes.

    Parameters:
        soup_obj (Optional[BeautifulSoup]): The BeautifulSoup object to search in.
        css_selector_ele (Optional[str]): CSS selector to get a list of matching elements.
        css_selector (Optional[str]): CSS selector to get a single element's content.
        attr (Optional[str]): Attribute name to extract from the selected element.

    Returns:
        Optional[Union[str, List[BeautifulSoup]]]: Extracted content based on the specified criteria.
            - If `css_selector_ele` is provided, returns a list of elements.
            - If `css_selector` is provided with or without `attr`, returns text or attribute value.
            - If no specific selector or attribute is provided, returns the text content of the soup object.
            - Returns `None` if no matching elements are found or inputs are invalid.
    """
    if soup_obj is None:
        return None  # No soup object provided.

    try:
        # Return a list of matching elements if `css_selector_ele` is provided.
        if css_selector_ele is not None and css_selector is None and attr is None:
            return soup_obj.select(css_selector_ele)

        # Return the text content of the first matching element for `css_selector`.
        elif css_selector is not None and css_selector_ele is None and attr is None:
            element = soup_obj.select_one(css_selector)
            return standardized_string(element.text) if element else None

        # Return the value of the specified attribute for `css_selector`.
        elif css_selector is not None and attr is not None and css_selector_ele is None:
            element = soup_obj.select_one(css_selector)
            return standardized_string(element.get(attr, "")) if element else None

        # Return the value of the specified attribute from the `soup_obj` directly.
        elif attr is not None and css_selector_ele is None and css_selector is None:
            return standardized_string(soup_obj.get(attr, ""))

        # Return the text content of the entire `soup_obj` if no selectors or attributes are provided.
        elif attr is None and css_selector_ele is None and css_selector is None:
            return standardized_string(soup_obj.text)
        else:
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def get_xpath_content(page_source: Optional[str] = None, xpath: Optional[str] = None, attr: Optional[str] = None) -> \
        Optional[str]:
    """
    Extracts content from an XPath expression in the given tree.

    Args:
        tree (Optional[Any]): The tree object (parsed HTML/XML) to search in. It could be a lxml.etree object or similar.
        xpath (Optional[str]): The XPath expression to query the tree. Default is None.
        attr (Optional[str]): The attribute name to retrieve from the matched element. Default is None.

    Returns:
        Optional[str]: The attribute value or text content of the first match, or an empty string if not found, or None if tree is None.
        page_source: is html content:
    """
    if page_source is None:
        return None

    # If tree is not a lxml Element, try to convert it
    if not isinstance(page_source, etree._Element):
        tree = get_html_object(page_source=page_source, lxml_tree_obj=True)
    tree = page_source
    if xpath is not None and attr is not None:
        try:
            # Attempt to retrieve the specified attribute
            return standardized_string(tree.xpath(xpath)[0].get(attr))
        except Exception:
            return ""  # Return an empty string if there is Any error in extracting the attribute
    elif xpath is not None and attr is None:
        try:
            # Attempt to retrieve the text content from the matched element
            return standardized_string(tree.xpath(xpath)[0].text)
        except:
            return ""  # Return an empty string if there is Any error in extracting the text
    return None  # Return None if neither xpath nor attr are specified


def remove_common_elements(remove_in: Union[list, tuple, set] = None,
                           remove_by: Union[list, tuple, set] = None) -> list:
    """
    Removes elements from `remove_in` that are present in `remove_by`.

    Args:
    - remove_in (Union[list, tuple, set], optional): The collection from which elements will be removed. Defaults to None.
    - remove_by (Union[list, tuple, set], optional): The collection containing elements to remove from `remove_in`. Defaults to None.

    Returns:
    - list: A list containing elements from `remove_in` that are not in `remove_by`.
    """
    if remove_in is not None and remove_by is not None:
        # Ensure both collections are sets for efficient difference operation
        set_a = remove_in
        set_b = remove_by

        if not isinstance(set_a, set):
            set_a = set(set_a)
        if not isinstance(set_b, set):
            set_b = set(set_b)

        set_a.difference_update(set_b)  # Remove elements from set_a that are in set_b
        return list(set_a)  # Return the result as a list

    else:
        missing_args = []
        if remove_in is None:
            missing_args.append('remove_in')
        if remove_by is None:
            missing_args.append('remove_by')

        print(f"Value not passed for: {', '.join(missing_args)}")
        return []


def read_csv(csv_file_path: str, get_value_by_col_name: Optional[str] = None, filter_col_name: Optional[str] = None,
             inculde_filter_col_values: Optional[List[str]] = None,
             exclude_filter_col_values: Optional[List[str]] = None, sep: str = ",") -> Union[List[str], pd.DataFrame]:
    """
    Reads a CSV file and returns values from a specific column based on various filters.

    Args:
    - csv_file_path (str): Path to the CSV file.
    - get_value_by_col_name (Optional[str]): The column name from which to fetch values.
    - filter_col_name (Optional[str]): The column name to apply filters.
    - inculde_filter_col_values (Optional[List[str]]): List of values to include in the filter.
    - exclude_filter_col_values (Optional[List[str]]): List of values to exclude from the filter.
    - sep (str, optional): The delimiter used in the CSV file. Defaults to "," (comma).

    Returns:
    - Union[List[str], pd.DataFrame]: A list of values if filtering, or the full DataFrame if no filtering.
    """

    if not os.path.exists(csv_file_path):
        print("read_csv: csv_file_path does not exist.")
        return []

    urls = []

    try:
        # Try to read CSV with error handling and the specified separator
        df = pd.read_csv(csv_file_path, header=0, sep=sep, encoding='utf-8', on_bad_lines='skip', dtype=object).fillna(
            "")

        if get_value_by_col_name and filter_col_name:
            # If we are filtering by include values
            if inculde_filter_col_values:
                for value in inculde_filter_col_values:
                    filtered_df = df[df[filter_col_name] == str(value)]
                    urls.extend(filtered_df[get_value_by_col_name].tolist())

            # If we are filtering by exclude values
            elif exclude_filter_col_values:
                for value in exclude_filter_col_values:
                    filtered_df = df[df[filter_col_name] != str(value)]
                    urls.extend(filtered_df[get_value_by_col_name].tolist())

        elif get_value_by_col_name and not filter_col_name:
            # If just getting values from a single column without filters
            urls.extend(df[get_value_by_col_name].tolist())

        elif not get_value_by_col_name and not filter_col_name:
            # If no filters or specific column is provided, return the entire DataFrame
            return df

        else:
            print("========= Arguments are not proper =========")
            return []

    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        return []

    # Return unique values (set removes duplicates) as a list
    return list(set(urls))


def save_to_csv(data_list: Optional[List[list]] = None, column_header_list: Optional[List[str]] = None,
                output_file_path: Optional[str] = None, sep: str = ",") -> None:
    """
    Saves data to a CSV file. If the file exists, it appends the data; otherwise, it creates a new file.

    Args:
    - data_list (Optional[List[list]], optional): The data to be saved in the CSV file. Defaults to None.
    - column_header_list (Optional[List[str]], optional): The column headers for the CSV file. Defaults to None.
    - output_file_path (Optional[str], optional): The path to the output CSV file. Defaults to None.
    - sep (str, optional): The delimiter used in the CSV file. Defaults to "," (comma).

    Returns:
    - None: This function doesn't return anything. It performs a side effect (writing to a file).
    """
    
    # Get the directory name from the full file path
    dir_name = get_dir_by_path(file_path=output_file_path)
    # Create the directory if it doesn't exist
    create_directory(directory_name=dir_name)

    if data_list and column_header_list and output_file_path:
        try:
            # Check if the file exists
            if os.path.exists(output_file_path):
                # Append data to the file if it exists
                pd.DataFrame(data_list, columns=column_header_list).to_csv(output_file_path, index=False, header=False,
                                                                           sep=sep, encoding="utf-8",
                                                                           quoting=csv.QUOTE_ALL, quotechar='"',
                                                                           mode="a")
            else:
                # Create a new file and write data
                pd.DataFrame(data_list, columns=column_header_list).to_csv(output_file_path, index=False, header=True,
                                                                           sep=sep, encoding="utf-8",
                                                                           quoting=csv.QUOTE_ALL, quotechar='"',
                                                                           mode="w")
        except Exception as e:
            print(f"save_to_csv: {e.__class__} - {str(e)}")
    else:
        missing_args = []
        if data_list is None:
            missing_args.append('data_list')
        if column_header_list is None:
            missing_args.append('column_header_list')
        if output_file_path is None:
            missing_args.append('output_file_path')

        print(f"Data not saved due to missing arguments: {', '.join(missing_args)}")


def save_to_xls(data_list: Optional[List[list]] = None, column_header_list: Optional[List[str]] = None,
                output_file_path: Optional[str] = None) -> None:
    """
    Saves data to an Excel (.xls) file. If the file exists, it appends the data; otherwise, it creates a new file.

    Args:
    - data_list (Optional[List[list]], optional): The data to be saved in the Excel file. Defaults to None.
    - column_header_list (Optional[List[str]], optional): The column headers for the Excel file. Defaults to None.
    - output_file_path (Optional[str], optional): The path to the output Excel file. Defaults to None.

    Returns:
    - None: This function doesn't return anything. It performs a side effect (writing to a file).
    """
    
    # Get the directory name from the full file path
    dir_name = get_dir_by_path(file_path=output_file_path)
    # Create the directory if it doesn't exist
    create_directory(directory_name=dir_name)

    if data_list and column_header_list and output_file_path:
        try:
            # Check if the file exists
            if os.path.exists(output_file_path):
                # If the file exists, load the existing content and append new data
                with pd.ExcelWriter(output_file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                    df = pd.DataFrame(data_list, columns=column_header_list)
                    df.to_excel(writer, index=False, header=False, sheet_name='Sheet1', startrow=writer.sheets['Sheet1'].max_row)
            else:
                # Create a new Excel file and write data
                with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
                    df = pd.DataFrame(data_list, columns=column_header_list)
                    df.to_excel(writer, index=False, header=True, sheet_name='Sheet1')
        except Exception as e:
            print(f"save_to_xls: {e.__class__} - {str(e)}")
    else:
        missing_args = []
        if data_list is None:
            missing_args.append('data_list')
        if column_header_list is None:
            missing_args.append('column_header_list')
        if output_file_path is None:
            missing_args.append('output_file_path')

        print(f"Data not saved due to missing arguments: {', '.join(missing_args)}")


def get_dir_by_path(file_path: str = None) -> Any:
    directory_path = os.path.dirname(file_path)  # Get the directory path
    return directory_path


def get_file_name_by_path(file_path: str = None) -> Any:
    file_name = os.path.basename(file_path)  # Get the file name
    return file_name

def get_list_files(directory: str, extension: Optional[str] = None) -> List[str]:
    """
    List files in a given directory, optionally filtering by file extension.

    :param directory: Path to the directory.
    :param extension: File extension to filter by (e.g., 'pdf'). Default is None (returns all files).
    :return: List of matching file names.
    """
    if extension:
        return [f for f in os.listdir(directory) if f.endswith(f'.{extension.strip(".")}') and os.path.isfile(os.path.join(directory, f))]
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


# Function to save content to a specified file path
def save_file(output_file_path: str = None, content: Any = "", encoding: str = "utf-8", mode: str = "w") -> None:
    if output_file_path is None:
        return

    try:
        # Get the directory name from the full file path
        dir_name = get_dir_by_path(file_path=output_file_path)

        # Get the file name from the full file path
        file_name = get_file_name_by_path(file_path=output_file_path)

        # Create the directory if it doesn't exist
        create_directory(directory_name=dir_name)

        # Rebuild the full output file path (in case the directory was created)
        output_file_path = os.path.join(dir_name, file_name)

        # Open the file in the specified mode and encoding, and save the content
        with open(output_file_path, mode, encoding=encoding) as file:
            if file_name.endswith(".json"):
                if content is None:
                    content = {}
                json.dump(content, file, indent=4)  # Format JSON with an indent of 4 spaces
                print(f"JSON content successfully written to {output_file_path}")
            else:
                if not isinstance(content, str):
                    content = str(content)
                file.write(content)  # Write the provided content to the file
                print(f"Content successfully written to {output_file_path}")

    except Exception as e:
        print(e)


def read_file(input_file_path: str = None, encoding: str = 'utf-8', mode: str = "r") -> Any:
    """
    Reads the content of a file, either as plain text or JSON, based on the file extension.

    Parameters:
        input_file_path (str): The path to the file to be read.
        encoding (str): The encoding used to read the file. Default is 'utf-8'.
        mode (str): The mode in which to open the file. Default is 'r' (read).

    Returns:
        Union[str, dict, None]: The content of the file. Returns a string for text files, 
                                 a dictionary for JSON files, or None if an error occurs.
    """
    try:
        # Ensure the file exists
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"The file '{input_file_path}' does not exist.")

        # Read and return the file content
        with open(input_file_path, mode, encoding=encoding) as file:
            if input_file_path.endswith(".json"):
                content = json.load(file)
                return content  # Return as dictionary if JSON file
            content = file.read()
            return content  # Return as string for regular text files
    except Exception as e:
        print(f"{e}")

def get_decoded_url(encoded_url: str) -> str:
    """
    Decodes a URL that contains Unicode escape sequences and percent-encoded characters.

    Args:
    encoded_url (str): The encoded URL string to be decoded.

    Returns:
    str: The fully decoded URL.

    Raises:
    ValueError: If the input is not a valid encoded URL.
    """
    try:
        # Use json.loads to decode the Unicode escape sequences (e.g., \u002F -> /)
        decoded_unicode_url = json.loads(f'"{encoded_url}"')
        
        # Then, decode any percent-encoded characters (e.g., %20 -> ' ')
        decoded_url = urllib.parse.unquote(decoded_unicode_url)
        
        return decoded_url

    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding URL: Invalid escape sequence in the URL. {e}")
    except Exception as e:
        raise ValueError(f"An error occurred while decoding the URL: {e}")
