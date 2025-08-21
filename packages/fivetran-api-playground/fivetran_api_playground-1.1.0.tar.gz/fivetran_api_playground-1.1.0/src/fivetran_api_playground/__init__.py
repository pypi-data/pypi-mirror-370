import base64
import os
import time
import uuid
import argparse
from flask import Flask, jsonify, request, Response, make_response, abort
import requests as rq
from faker import Faker
from datetime import datetime, timedelta
import random
from collections import OrderedDict
import json

__version__ = "1.1.0"

__API_KEY_OR_FORMAT = "Invalid API key or format"
__HEADER_IS_MISSING = "Authorization header is missing"

app = Flask(__name__)
fake = Faker()

items = []
companies = []
departments_by_company = {}
MAX_RECORDS = 200  # Total Records that API will serve for each endpoint
NUM_COMPANIES = 2  # Number of companies to generate
DEPARTMENTS_PER_COMPANY = 4
DEPARTMENT_NAMES = ["Engineering", "HR", "Finance", "Sales"]
DEFAULT_ORDER_BY = 'updatedAt'
DEFAULT_ORDER_TYPE = 'asc'
DEFAULT_PAGE_SIZE = 10

ROOT_LOCATION = ".ft_api_playground"
LAST_VERSION_CHECK_FILE = "_last_version_check"
ONE_DAY_IN_SEC = 24 * 60 * 60
VALID_COMMANDS = ["start"]
DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
DATE_TIME_FORMAT_WITHOUT_Z = "%Y-%m-%dT%H:%M:%S"
APPLICATION_JSON = 'application/json'
INVALID_DATE_FORMAT_MESSAGE = "Invalid date format for 'updated_since'. Use 'YYYY-MM-DDTHH:MM:SSZ'"
INVALID_ORDER_BY_MESSAGE = "Invalid value for 'order_by'. Use 'createdAt' or 'updatedAt'"
INVALID_ORDER_TYPE_MESSAGE = "Invalid value for 'order_type'. Use 'asc' or 'desc'"
INVALID_DATE_FORMAT_MISSING_Z_MESSAGE = "Invalid date format for 'updated_since'. Must end with 'Z' for UTC"
PYPI_PACKAGE_DETAILS_URL = "https://pypi.org/pypi/fivetran_api_playground/json"
MAX_RETRIES = 3

# Generated Authentication Keys
# HTTP_BASIC
HTTP_BASIC_USERNAME = str(uuid.uuid4()).replace('-', '')[:5] + '@example.com'
HTTP_BASIC_PASSWORD = str(uuid.uuid4()).replace('-', '')[:8]
# HTTP_BEARER
HTTP_BEARER_TOKEN = str(uuid.uuid4())
# API_KEY
API_KEY = str(uuid.uuid4())
# SESSION_AUTH
SESSION_AUTH_USERNAME = str(uuid.uuid4()).replace('-', '')[:5] + '@example.com'
SESSION_AUTH_PASSWORD = str(uuid.uuid4()).replace('-', '')[:10]

for index in range(MAX_RECORDS):
    record_creation_time = datetime.now() - timedelta(hours=MAX_RECORDS - index, minutes=random.randint(0, 59),
                                                      seconds=random.randint(0, 59))
    user = OrderedDict([
        ('id', str(uuid.uuid4())),
        ('name', fake.name()),
        ('email', fake.email()),
        ('address', fake.address()),
        ('company', fake.company()),
        ('job', fake.job()),
        ('createdAt', record_creation_time.strftime(
            DATE_TIME_FORMAT)),
        ('updatedAt',
         (record_creation_time + timedelta(minutes=random.randint(0, 59), seconds=random.randint(0, 59))).strftime(
             DATE_TIME_FORMAT))
    ])
    items.append(user)

for index in range(NUM_COMPANIES):
    record_creation_time = datetime.now() - timedelta(hours=MAX_RECORDS - index, minutes=random.randint(0, 59),
                                                      seconds=random.randint(0, 59))
    company = OrderedDict([
        ('company_id', index+1),
        ('company_name', fake.company()),
        ('createdAt', record_creation_time.strftime(
            DATE_TIME_FORMAT)),
        ('updatedAt',
         (record_creation_time + timedelta(minutes=random.randint(0, 59), seconds=random.randint(0, 59))).strftime(
             DATE_TIME_FORMAT))
    ])
    companies.append(company)

    department_list = []
    for department_index in range(DEPARTMENTS_PER_COMPANY):
        department = OrderedDict([
            ('department_id', department_index + 1),
            ('company_id', index+1),
            ('department_name', DEPARTMENT_NAMES[department_index]),
            ('createdAt', record_creation_time.strftime(
                DATE_TIME_FORMAT)),
            ('updatedAt',
             (record_creation_time + timedelta(minutes=random.randint(0, 59), seconds=random.randint(0, 59))).strftime(
                 DATE_TIME_FORMAT))
        ])
        department_list.append(department)

    departments_by_company[index+1] = department_list

# Custom JSON encoder to preserve order in API Response
class CustomJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, OrderedDict):
            return json.dumps(obj, indent=4, separators=(',', ': '))
        return super().encode(obj)


@app.route('/pagination/next_page_url', methods=['GET'])
def get_next_page_url_pagination():
    allowed_params = {'order_by', 'order_type', 'per_page', 'updated_since', 'page'}

    # Get filters from query parameters
    received_params = set(request.args.keys())

    # Throw an error if any unexpected parameters are passed
    unexpected_params = received_params - allowed_params
    if unexpected_params:
        return jsonify({'error': f'Unexpected query parameters: {", ".join(unexpected_params)}'}), 400

    # Get allowed filters from query parameters
    order_by_arg = request.args.get('order_by', type=str, default=DEFAULT_ORDER_BY)  # createdAt, updatedAt [Default
    # updatedAt]
    order_type_arg = request.args.get('order_type', type=str, default=DEFAULT_ORDER_TYPE)  # asc, desc [Default asc]
    per_page_arg = request.args.get('per_page', type=int, default=DEFAULT_PAGE_SIZE)  # [1-50] Default 10
    updated_since_arg = request.args.get('updated_since', type=str)

    # Validate order_by value
    if order_by_arg not in ['createdAt', 'updatedAt']:
        return jsonify({"error": INVALID_ORDER_BY_MESSAGE}), 400

    # Validate order_type value
    if order_type_arg not in ['asc', 'desc']:
        return jsonify({"error": INVALID_ORDER_TYPE_MESSAGE}), 400

    # Validate per_page value
    if not (1 <= per_page_arg <= 50):
        return jsonify({"error": "Invalid value for 'per_page'. It should be between 1 and 50."}), 400

    # Filter items based on the updated_since parameter
    filtered_items = items
    if updated_since_arg:
        try:
            # Ensure the format ends with 'Z' indicating UTC
            if updated_since_arg.endswith('Z'):
                updated_since_arg = updated_since_arg[:-1]  # Strip the 'Z' before parsing
                updated_since_date = datetime.strptime(updated_since_arg, DATE_TIME_FORMAT_WITHOUT_Z)
                updated_since_date = updated_since_date.replace(tzinfo=None)  # Set the timezone to UTC
            else:
                return jsonify({"error": INVALID_DATE_FORMAT_MISSING_Z_MESSAGE}), 400

            # Convert 'updatedAt' to datetime for comparison
            filtered_items = [item for item in items if
                              datetime.strptime(item['updatedAt'][:-1], DATE_TIME_FORMAT_WITHOUT_Z)
                              >= updated_since_date]
        except ValueError:
            return jsonify({"error": INVALID_DATE_FORMAT_MESSAGE}), 400

    # Sort the filtered items
    reverse_order = (order_type_arg == 'desc')
    filtered_items.sort(key=lambda x: x[order_by_arg], reverse=reverse_order)

    # Pagination logic
    page = request.args.get('page', default=1, type=int)
    start_index = (page - 1) * per_page_arg
    end_index = start_index + per_page_arg
    paginated_items = filtered_items[start_index:end_index]

    # Next page logic
    next_page_url = None
    if end_index < len(filtered_items):
        next_page_url = f"{request.base_url}?page={page + 1}&per_page={per_page_arg}&order_by={order_by_arg}&order_type={order_type_arg}"
        if updated_since_arg:
            next_page_url += f"&updated_since={updated_since_arg}Z"  # Add 'Z' back for the next page

    response = {
        'data': paginated_items,
        'total_items': len(filtered_items),
        'page': page,
        'per_page': per_page_arg,
        'next_page_url': next_page_url
    }

    return Response(json.dumps(response, cls=CustomJSONEncoder), mimetype=APPLICATION_JSON)


@app.route('/pagination/page_number', methods=['GET'])
def get_page_number_pagination():
    allowed_params = {'order_by', 'order_type', 'per_page', 'page', 'updated_since'}

    # Get filters from query parameters
    received_params = set(request.args.keys())

    # Throw an error if any unexpected parameters are passed
    unexpected_params = received_params - allowed_params
    if unexpected_params:
        return jsonify({'error': f'Unexpected query parameters: {", ".join(unexpected_params)}'}), 400

    # Get allowed filters from query parameters
    order_by_arg = request.args.get('order_by', type=str, default=DEFAULT_ORDER_BY)  # Default to updatedAt
    order_type_arg = request.args.get('order_type', type=str, default=DEFAULT_ORDER_TYPE)  # Default to asc
    per_page_arg = request.args.get('per_page', type=int, default=DEFAULT_PAGE_SIZE)  # Default to 10
    page_arg = request.args.get('page', default=1, type=int)  # Default to page 1
    updated_since_arg = request.args.get('updated_since', type=str)

    # Validate `order_by` value
    if order_by_arg not in ['createdAt', 'updatedAt']:
        return jsonify({"error": INVALID_ORDER_BY_MESSAGE}), 400

    # Validate `order_type` value
    if order_type_arg not in ['asc', 'desc']:
        return jsonify({"error": INVALID_ORDER_TYPE_MESSAGE}), 400

    # Validate `per_page` value
    if not (1 <= per_page_arg <= 50):
        return jsonify({"error": "Invalid value for 'per_page'. It should be between 1 and 50."}), 400

    # Validate `page` value
    if page_arg < 1:
        return jsonify({"error": "Invalid value for 'page'. It must be greater than or equal to 1."}), 400

    # Filter items based on the updated_since parameter
    filtered_items = items
    if updated_since_arg:
        try:
            if updated_since_arg.endswith('Z'):
                updated_since_arg = updated_since_arg[:-1]  # Strip the 'Z' before parsing
                updated_since_date = datetime.strptime(updated_since_arg, DATE_TIME_FORMAT_WITHOUT_Z)
                updated_since_date = updated_since_date.replace(tzinfo=None)  # Set the timezone to UTC
            else:
                return jsonify({"error": INVALID_DATE_FORMAT_MISSING_Z_MESSAGE}), 400

            # Filter items
            filtered_items = [item for item in items if
                              datetime.strptime(item['updatedAt'][:-1],
                                                DATE_TIME_FORMAT_WITHOUT_Z) >= updated_since_date]
        except ValueError:
            return jsonify({"error": INVALID_DATE_FORMAT_MESSAGE}), 400

    # Sort the filtered items
    reverse_order = (order_type_arg == 'desc')
    filtered_items.sort(key=lambda x: x[order_by_arg], reverse=reverse_order)

    # Pagination logic
    start_index = (page_arg - 1) * per_page_arg
    end_index = start_index + per_page_arg
    paginated_items = filtered_items[start_index:end_index]

    # Total pages calculation
    total_items = len(filtered_items)
    total_pages = (total_items + per_page_arg - 1) // per_page_arg  # Calculate total pages

    # Prepare the response
    response = {
        'data': paginated_items,
        'page': page_arg,
        'page_size': per_page_arg,
        'total_pages': total_pages,
        'total_items': total_items  # Optional total items count
    }

    return Response(json.dumps(response, cls=CustomJSONEncoder), mimetype=APPLICATION_JSON)


@app.route('/pagination/offset', methods=['GET'])
def get_offset_pagination():
    allowed_params = {'order_by', 'order_type', 'limit', 'offset', 'updated_since'}

    # Get filters from query parameters
    received_params = set(request.args.keys())

    # Throw an error if any unexpected parameters are passed
    unexpected_params = received_params - allowed_params
    if unexpected_params:
        return jsonify({'error': f'Unexpected query parameters: {", ".join(unexpected_params)}'}), 400

    # Get allowed filters from query parameters
    order_by_arg = request.args.get('order_by', type=str, default=DEFAULT_ORDER_BY)  # Default to updatedAt
    order_type_arg = request.args.get('order_type', type=str, default=DEFAULT_ORDER_TYPE)  # Default to asc
    limit_arg = request.args.get('limit', type=int, default=DEFAULT_PAGE_SIZE)  # Default to 10
    offset_arg = request.args.get('offset', type=int, default=0)  # Default to 0
    updated_since_arg = request.args.get('updated_since', type=str)

    # Validate `limit` value
    if not (1 <= limit_arg <= 50):
        return jsonify({"error": "Invalid value for 'limit'. It should be between 1 and 50."}), 400

    # Validate `offset` value
    if offset_arg < 0:
        return jsonify({"error": "Invalid value for 'offset'. It must be greater than or equal to 0."}), 400

    # Validate `order_by` value
    if order_by_arg not in ['createdAt', 'updatedAt']:
        return jsonify({"error": INVALID_ORDER_BY_MESSAGE}), 400

    # Validate `order_type` value
    if order_type_arg not in ['asc', 'desc']:
        return jsonify({"error": INVALID_ORDER_TYPE_MESSAGE}), 400

    # Filter items based on the updated_since parameter
    filtered_items = items
    if updated_since_arg:
        try:
            if updated_since_arg.endswith('Z'):
                updated_since_arg = updated_since_arg[:-1]  # Strip the 'Z' before parsing
                updated_since_date = datetime.strptime(updated_since_arg, DATE_TIME_FORMAT_WITHOUT_Z)
                updated_since_date = updated_since_date.replace(tzinfo=None)  # Set the timezone to UTC
            else:
                return jsonify({"error": INVALID_DATE_FORMAT_MISSING_Z_MESSAGE}), 400

            # Filter items
            filtered_items = [item for item in items if
                              datetime.strptime(item['updatedAt'][:-1],
                                                DATE_TIME_FORMAT_WITHOUT_Z) >= updated_since_date]
        except ValueError:
            return jsonify({"error": INVALID_DATE_FORMAT_MESSAGE}), 400

    # Sort the filtered items
    reverse_order = (order_type_arg == 'desc')
    filtered_items.sort(key=lambda x: x[order_by_arg], reverse=reverse_order)

    # Calculate total items after filtering
    total_items = len(filtered_items)

    # Calculate the data slice based on offset and limit
    paginated_items = filtered_items[offset_arg:offset_arg + limit_arg]

    # Prepare the response
    response = {
        'data': paginated_items,
        'offset': offset_arg,
        'limit': limit_arg,
        'total': total_items  # Total number of items
    }

    return Response(json.dumps(response, cls=CustomJSONEncoder), mimetype=APPLICATION_JSON)


@app.route('/pagination/keyset', methods=['GET'])
def get_keyset_pagination():
    page_size = 5 * DEFAULT_PAGE_SIZE

    allowed_params = {'scroll_param', 'updated_since'}

    # Get filters from query parameters
    received_params = set(request.args.keys())

    # Throw an error if any unexpected parameters are passed
    unexpected_params = received_params - allowed_params
    if unexpected_params:
        return jsonify({'error': f'Unexpected query parameters: {", ".join(unexpected_params)}'}), 400

    # Get allowed request parameters
    scroll_param = request.args.get('scroll_param', type=str)
    updated_since_arg = request.args.get('updated_since', type=str)

    # Ensure that both `scroll_param` and `updated_since` are not used together
    if scroll_param and updated_since_arg:
        return jsonify({"error": "You can only use 'updated_since' in first request, subsequent requests should use "
                                 "only 'scroll_param'"}), 400

    # Filter items
    filtered_items = items

    # Handle the first request with `updated_since`
    if updated_since_arg:
        try:
            if updated_since_arg.endswith('Z'):
                updated_since_arg = updated_since_arg[:-1]  # Strip the 'Z'
                updated_since_date = datetime.strptime(updated_since_arg, DATE_TIME_FORMAT_WITHOUT_Z)
            else:
                return jsonify({"error": INVALID_DATE_FORMAT_MISSING_Z_MESSAGE}), 400

            # Filter based on `updatedAt`
            filtered_items = [item for item in items if
                              datetime.strptime(item['updatedAt'][:-1],
                                                DATE_TIME_FORMAT_WITHOUT_Z) >= updated_since_date]
        except ValueError:
            return jsonify({"error": ("%s" % INVALID_DATE_FORMAT_MESSAGE)}), 400

    # Handle subsequent requests with `scroll_param`
    elif scroll_param:
        try:
            # Decode the base64 encoded `scroll_param`
            decoded_param = base64.b64decode(scroll_param).decode('utf-8')
            scroll_date = datetime.strptime(decoded_param, (DATE_TIME_FORMAT))

            # Filter items based on `updatedAt` for keyset pagination
            filtered_items = [item for item in items if
                              datetime.strptime(item['updatedAt'][:-1], DATE_TIME_FORMAT_WITHOUT_Z) > scroll_date]
        except ValueError:
            return jsonify({"error": "Invalid scroll_param value"}), 400

    # Sort the filtered items by `updatedAt` in ascending order
    filtered_items.sort(key=lambda x: x['updatedAt'])

    # Limit the number of items returned (for example, 10 items per page)
    per_page_arg = request.args.get('per_page', type=int, default=page_size)
    paginated_items = filtered_items[:per_page_arg]

    # Generate the next `scroll_param` if there are more items
    next_scroll_param = None
    if len(filtered_items) > per_page_arg:
        last_item_updated_at = paginated_items[-1]['updatedAt']
        next_scroll_param = base64.b64encode(last_item_updated_at.encode('utf-8')).decode('utf-8')

    # Prepare the response
    response = {
        'data': paginated_items,
        'scroll_param': next_scroll_param
    }

    return Response(json.dumps(response, cls=CustomJSONEncoder), mimetype=APPLICATION_JSON)


def check_newer_version():
    root_dir = os.path.join(os.path.expanduser("~"), ROOT_LOCATION)
    last_check_file_path = os.path.join(root_dir, LAST_VERSION_CHECK_FILE)
    if not os.path.isdir(root_dir):
        os.makedirs(root_dir, exist_ok=True)

    if os.path.isfile(last_check_file_path):
        # Is it time to check again?
        with open(last_check_file_path, 'r') as f_in:
            timestamp = int(f_in.read())
            if (int(time.time()) - timestamp) < ONE_DAY_IN_SEC:
                return

    for index in range(MAX_RETRIES):
        try:
            # check version and save current time
            response = rq.get(PYPI_PACKAGE_DETAILS_URL)
            response.raise_for_status()
            data = json.loads(response.text)
            latest_version = data["info"]["version"]
            if __version__ < latest_version:
                print("[notice] A new release of 'fivetran-api-playground' is available: {}".format(latest_version))
                print("[notice] To update, run: pip install --upgrade fivetran-api-playground")

            with open(last_check_file_path, 'w') as f_out:
                f_out.write(f"{int(time.time())}")
            break
        except Exception:
            retry_after = 2 ** index
            print(
                f"WARNING: Unable to check if a newer version of `fivetran-api-playground` is available. Retrying again after {retry_after} seconds")
            time.sleep(retry_after)


@app.route('/export/csv', methods=['GET'])
def export_data():
    if not items:
        return jsonify({"error": "No data available to export."}), 400

    # Create a response object to send the CSV file
    def generate_csv():
        # Write header
        header = items[0].keys()
        yield ','.join(header) + '\n'

        # Write data rows
        for record in items:
            yield f"{clean_string_for_csv(record['id'])},{clean_string_for_csv(record['name'])},{clean_string_for_csv(record['email'])},{clean_string_for_csv(record['address'])},{clean_string_for_csv(record['company'])},{clean_string_for_csv(record['job'])},{record['createdAt']},{record['updatedAt']}\n"

    # Generate the response with CSV content
    response = make_response(generate_csv())
    response.headers['Content-Disposition'] = 'attachment; filename=data_export.csv'
    response.headers['Content-Type'] = 'text/csv'

    return response

def clean_string_for_csv(input_string):
    return input_string.replace("\n", "").replace("\r", "").replace(",", "")

@app.route("/auth/http_basic", methods=["GET"])
def auth_http_basic():
    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        abort(401, description=__HEADER_IS_MISSING)

    # Extract the API key from the header (expected format: 'Basic <Base64(Username:Password)>')
    auth_string = f"{HTTP_BASIC_USERNAME}:{HTTP_BASIC_PASSWORD}"
    auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

    try:
        auth_type, auth_key = auth_header.split(" ", 1)
        if auth_type != "Basic" or auth_key != auth_base64:
            raise ValueError
    except ValueError:
        abort(401, description=__API_KEY_OR_FORMAT)

    # If API key is valid, return the data
    return jsonify({"data": items[:20]})

@app.route("/auth/http_bearer", methods=["GET"])
def auth_http_bearer():
    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        abort(401, description=__HEADER_IS_MISSING)

    # Extract the API key from the header (expected format: 'Bearer <BearerToken>')

    try:
        auth_type, auth_key = auth_header.split(" ", 1)
        if auth_type != "Bearer" or auth_key != HTTP_BEARER_TOKEN:
            raise ValueError
    except ValueError:
        abort(401, description=__API_KEY_OR_FORMAT)

    # If API key is valid, return the data
    return jsonify({"data": items[:20]})

@app.route("/auth/api_key", methods=["GET"])
def auth_api_key():
    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        abort(401, description=__HEADER_IS_MISSING)

    # Extract the API key from the header (expected format: 'apiKey <API_KEY>')

    try:
        auth_type, auth_key = auth_header.split(" ", 1)
        if auth_type != "apiKey" or auth_key != API_KEY:
            raise ValueError
    except ValueError:
        abort(401, description=__API_KEY_OR_FORMAT)

    # If API key is valid, return the data
    return jsonify({"data": items[:20]})

@app.route("/auth/session_token/login", methods=["POST"])
def auth_session_token_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Validate that username and password are provided
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Assuming username and password are correct
    if username == SESSION_AUTH_USERNAME and password == SESSION_AUTH_PASSWORD:
        # Create a base64 encoded string: username:password
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

        # Return the encoded credentials as JSON response
        return jsonify({'token': encoded_credentials}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/auth/session_token/data', methods=['GET'])
def auth_session_token_data():
    # Extract token from Authorization header
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token is missing'}), 400

    try:
        # Remove "Token " prefix from token if it exists
        if token.startswith("Token "):
            token = token[6:]

        # Decode the Base64 encoded token
        decoded_credentials = base64.b64decode(token).decode('utf-8')
        username, password = decoded_credentials.split(":")

        # Validate the decoded credentials
        if username == SESSION_AUTH_USERNAME and password == SESSION_AUTH_PASSWORD:

            return jsonify({"data": items[:20]})
        else:
            return jsonify({'error': 'Invalid Token'}), 401

    except Exception:
        return jsonify({'error': 'Invalid token format'}), 400

@app.route('/cursors/companies', methods=['GET'])
def get_companies_cursors():
    allowed_params = {'order_by', 'order_type', 'updated_since'}

    # Get filters from query parameters
    received_params = set(request.args.keys())

    # Throw an error if any unexpected parameters are passed
    unexpected_params = received_params - allowed_params
    if unexpected_params:
        return jsonify({'error': f'Unexpected query parameters: {", ".join(unexpected_params)}'}), 400

    # Get allowed filters from query parameters
    order_by_arg = request.args.get('order_by', type=str, default=DEFAULT_ORDER_BY)  # createdAt, updatedAt [Default
    # updatedAt]
    order_type_arg = request.args.get('order_type', type=str, default=DEFAULT_ORDER_TYPE)  # asc, desc [Default asc]
    updated_since_arg = request.args.get('updated_since', type=str)

    # Validate order_by value
    if order_by_arg not in ['createdAt', 'updatedAt']:
        return jsonify({"error": INVALID_ORDER_BY_MESSAGE}), 400

    # Validate order_type value
    if order_type_arg not in ['asc', 'desc']:
        return jsonify({"error": INVALID_ORDER_TYPE_MESSAGE}), 400

    # Filter items based on the updated_since parameter
    filtered_companies = companies
    if updated_since_arg:
        try:
            # Ensure the format ends with 'Z' indicating UTC
            if updated_since_arg.endswith('Z'):
                updated_since_arg = updated_since_arg[:-1]  # Strip the 'Z' before parsing
                updated_since_date = datetime.strptime(updated_since_arg, DATE_TIME_FORMAT_WITHOUT_Z)
                updated_since_date = updated_since_date.replace(tzinfo=None)  # Set the timezone to UTC
            else:
                return jsonify({"error": INVALID_DATE_FORMAT_MISSING_Z_MESSAGE}), 400

            # Convert 'updatedAt' to datetime for comparison
            filtered_companies = [company for company in companies if
                              datetime.strptime(company['updatedAt'][:-1], DATE_TIME_FORMAT_WITHOUT_Z)
                              >= updated_since_date]
        except ValueError:
            return jsonify({"error": INVALID_DATE_FORMAT_MESSAGE}), 400

    # Sort the filtered items
    reverse_order = (order_type_arg == 'desc')
    filtered_companies.sort(key=lambda x: x[order_by_arg], reverse=reverse_order)

    response = {
        'data': filtered_companies,
        'total_items': len(filtered_companies),
    }

    # update the 'updatedAt' field for random companies to simulate changes
    for company in random.sample(companies, k=random.randint(0, NUM_COMPANIES)):
        company["updatedAt"] = datetime.now().strftime(DATE_TIME_FORMAT)

    return Response(json.dumps(response, cls=CustomJSONEncoder), mimetype=APPLICATION_JSON)

@app.route('/cursors/<company_id>/departments', methods=['GET'])
def get_department_by_companies(company_id):
    allowed_params = {'order_by', 'order_type', 'updated_since'}

    # Get filters from query parameters
    received_params = set(request.args.keys())

    # Throw an error if any unexpected parameters are passed
    unexpected_params = received_params - allowed_params
    if unexpected_params:
        return jsonify({'error': f'Unexpected query parameters: {", ".join(unexpected_params)}'}), 400

    # Get allowed filters from query parameters
    order_by_arg = request.args.get('order_by', type=str, default=DEFAULT_ORDER_BY)  # createdAt, updatedAt [Default
    # updatedAt]
    order_type_arg = request.args.get('order_type', type=str, default=DEFAULT_ORDER_TYPE)  # asc, desc [Default asc]
    updated_since_arg = request.args.get('updated_since', type=str)

    # Validate order_by value
    if order_by_arg not in ['createdAt', 'updatedAt']:
        return jsonify({"error": INVALID_ORDER_BY_MESSAGE}), 400

    # Validate order_type value
    if order_type_arg not in ['asc', 'desc']:
        return jsonify({"error": INVALID_ORDER_TYPE_MESSAGE}), 400

    try:
        company_id = int(company_id)
        if company_id not in departments_by_company:
            return jsonify({"error": f"company_id '{company_id}' not found"}), 404
    except ValueError:
        return jsonify({"error": "Invalid value for 'company_id'. 'company_id' must be an integer"}), 400

    # Filter items based on the updated_since parameter
    filtered_departments = departments_by_company[company_id]
    if updated_since_arg:
        try:
            # Ensure the format ends with 'Z' indicating UTC
            if updated_since_arg.endswith('Z'):
                updated_since_arg = updated_since_arg[:-1]  # Strip the 'Z' before parsing
                updated_since_date = datetime.strptime(updated_since_arg, DATE_TIME_FORMAT_WITHOUT_Z)
                updated_since_date = updated_since_date.replace(tzinfo=None)  # Set the timezone to UTC
            else:
                return jsonify({"error": INVALID_DATE_FORMAT_MISSING_Z_MESSAGE}), 400

            # Convert 'updatedAt' to datetime for comparison
            filtered_departments = [department for department in departments_by_company[company_id] if
                              datetime.strptime(department['updatedAt'][:-1], DATE_TIME_FORMAT_WITHOUT_Z)
                              >= updated_since_date]
        except ValueError:
            return jsonify({"error": INVALID_DATE_FORMAT_MESSAGE}), 400

    # Sort the filtered items
    reverse_order = (order_type_arg == 'desc')
    filtered_departments.sort(key=lambda x: x[order_by_arg], reverse=reverse_order)

    response = {
        'data': filtered_departments,
        'total_items': len(filtered_departments),
    }

    # update the 'updatedAt' field for random departments to simulate changes
    for department in random.sample(departments_by_company[company_id], k=random.randint(0, DEPARTMENTS_PER_COMPANY)):
        department["updatedAt"] = datetime.now().strftime(DATE_TIME_FORMAT)

    return Response(json.dumps(response, cls=CustomJSONEncoder), mimetype=APPLICATION_JSON)

def main():
    """The main entry point for the script.
    Parses command line arguments and passes them to connector object methods
    """

    parser = argparse.ArgumentParser(allow_abbrev=False)

    parser.add_argument("command", help="|".join(VALID_COMMANDS))
    parser.add_argument("--port", type=int, default=None, help="Provide the port on which you want to run the API on "
                                                               "localhost")
    args = parser.parse_args()
    port = args.port if args.port else 5001

    if args.command.lower() == "start":
        check_newer_version()
        print("Starting Local API on port " + str(port) + " ...\n")
        pagination_types = [
            "Next Page URL Pagination",
            "Page Number Pagination",
            "Offset Pagination",
            "Keyset Pagination"
        ]

        pagination_endpoints = [
            f"GET http://127.0.0.1:{port}/pagination/next_page_url",
            f"GET http://127.0.0.1:{port}/pagination/page_number",
            f"GET http://127.0.0.1:{port}/pagination/offset",
            f"GET http://127.0.0.1:{port}/pagination/keyset",
        ]

        api_endpoint_types = [
            "Export with CSV"
        ]
        api_endpoints = [
            f"GET http://127.0.0.1:{port}/export/csv",
        ]

        authentication_endpoint_types = [
            "Http Basic Auth",
            "HTTP Bearer",
            "Auth API Key",
            "Session Token Auth Login",
            "Session Token Auth Data"
        ]

        authentication_credentials = [
            f"Username: {HTTP_BASIC_USERNAME} Password: {HTTP_BASIC_PASSWORD}",
            f"Bearer Token: {HTTP_BEARER_TOKEN}",
            f"API Key: {API_KEY}",
            f"Username: {SESSION_AUTH_USERNAME}  Password: {SESSION_AUTH_PASSWORD}",
            "Use Token Received from Login endpoint"
        ]

        authentication_endpoints = [
            f"GET http://127.0.0.1:{port}/auth/http_basic",
            f"GET http://127.0.0.1:{port}/auth/http_bearer",
            f"GET http://127.0.0.1:{port}/auth/api_key",
            f"GET http://127.0.0.1:{port}/auth/session_token/login",
            f"GET http://127.0.0.1:{port}/auth/session_token/data"
        ]

        cursor_types = [
            "Companies Cursor",
            "Departments by Company Cursor"
        ]

        cursor_endpoints = [
            f"GET http://127.0.0.1:{port}/cursors/companies",
            f"GET http://127.0.0.1:{port}/cursors/<company_id>/departments"
        ]

        # Print header
        print("-" * 140)
        print(f"{'Pagination Type':<30} | {'Endpoint':<50}")
        print("-" * 140)
        # Print each pagination type and its corresponding endpoint
        for pagination_type, endpoint in zip(pagination_types, pagination_endpoints):
            print(f"{pagination_type:<30} | {endpoint:<50}")
        print("-" * 140)
        print()
        print("-" * 140)
        # Print header
        print(f"{'API Endpoint Type':<30} | {'Endpoint':<50}")
        print("-" * 140)
        # Print each api type and its corresponding endpoint
        for api_type, endpoint in zip(api_endpoint_types, api_endpoints):
            print(f"{api_type:<30} | {endpoint:<50}")
        print("-" * 140)
        print()
        print("-" * 140)
        # Print header
        print(f"{'Authentication Endpoint Type':<30} | {'Endpoint':<50} | {'Credentials':<50}")
        print("-" * 140)
        # Print each api type and its corresponding endpoint
        for auth_type, creds, endpoint in zip(authentication_endpoint_types, authentication_credentials, authentication_endpoints):
            print(f"{auth_type:<30} | {endpoint:<50} | {creds:<50}")
        print("-" * 140)
        print()
        print("-" * 140)
        # Print header
        print(f"{'Cursor Endpoint Type':<30} | {'Endpoint':<50}")
        print("-" * 140)
        # Print each cursor type and its corresponding endpoint
        for cursor_type, endpoint in zip(cursor_types, cursor_endpoints):
            print(f"{cursor_type:<30} | {endpoint:<50}")
        print("-" * 140)
        print("You can read about the API documentation for each endpoint on: \n"
              "https://pypi.org/project/fivetran-api-playground/")
        print("-" * 140)
        print("For your observability the API requests will be logged here!")
        print("Keep this process up and running until you finish trying out the API.\n")
        app.run(debug=True, port=port)

    else:
        raise NotImplementedError(f"Invalid command: {args.command}, see `api_playground --help`")


if __name__ == "__main__":
    main()
