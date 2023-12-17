import sqlite3
import urllib.parse
from functools import wraps
from itertools import combinations

from flask import redirect, render_template, request, session


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def printErrorMsgs(error) -> str:
    print(error)
    error_msg = ""
    error_messages = {
        "This field is required.": " is required.",
        "Not a valid integer value.": " must be a number.",
        "Number must be at least 0.": " must be a positive number.",
        "Number must be between 1 and 99.": " must be between 1 and 99.",
        "Choices cannot be None.": " cannot be empty.",
        "Field must be equal to password.": " must be equal to the password.",
        "Cheer and member cannot be the same": " Cheer and member cannot be the same.",
        "Total is not correct": "Total is not correct.",
    }

    for field in error:
        for key, value in error_messages.items():
            if key in error[field]:
                error_msg += f"The {field} field{value}\n "
            else:
                error_msg += f"{field}: {value}"

    print(error_msg)

    return error_msg


def get_theme_list(cursor: sqlite3.Cursor, user_id: str) -> list[str]:
    themes = cursor.execute(
        "select name from themes where user = ? or user = 0;", (user_id,)
    ).fetchall()
    themes = [str(item[0]) for item in themes]
    themes.append("(Other)")

    return themes


def get_member_list(cursor, user_id: str) -> list[str]:
    members = cursor.execute(
        "select member from members where user = ? or user = 0;", (user_id,)
    ).fetchall()
    members = [str(item[0]) for item in members]
    members.append("(Other)")

    return members


def log_app_data(*args, file_name="app_log.txt"):
    """
    Logs given data to a specified file. Handles strings and lists of dictionaries.

    Args:
    *args: Arbitrary number of arguments to be logged, expecting a string followed by lists of dictionaries.
    file_name (str): The name of the file to which the data will be logged. Defaults to 'app_log.txt'.
    """
    with open(file_name, "a") as file:
        for item in args:
            if isinstance(item, str):
                # Write strings directly
                file.write(item + "\n")
            elif isinstance(item, dict):
                # Write dictionaries directly
                file.write(str(item) + "\n")
            elif isinstance(item, list) and all(
                isinstance(elem, dict) for elem in item
            ):
                # Write each dictionary in the list on a new line
                for dict_item in item:
                    file.write(str(dict_item) + "\n")
            else:
                # Fallback for other data types
                file.write("Unsupported data type: " + str(type(item)) + "\n")
            file.write("\n")  # Add a newline to separate different calls


def convert_to_int(data: dict) -> dict:
    for key in data:
        if isinstance(data[key], float):
            data[key] = round(data[key])
    return data
