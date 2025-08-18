import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import requests
from PIL import Image
import io
import mimetypes
from urllib.parse import urlparse, urlencode

# --- Globals ---
mcp = FastMCP("LocalDemo")
CONFIG_PATH = Path.home() / ".mcp" / "strapi-mcp-server.config.json"

# --- Helper Functions ---

def _load_config():
    """Load the Strapi server configuration from the JSON file."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def _get_server_config(server_name: str):
    """Get the configuration for a specific server."""
    config = _load_config()
    server_config = config.get(server_name)
    if not server_config:
        raise ValueError(f"Server '{server_name}' not found in config. Available servers: {', '.join(config.keys())}")
    return server_config

def _make_strapi_request(server_name: str, endpoint: str, method: str = "GET", params: dict = None, json_body: dict = None, files: dict = None):
    """Make a generic request to the Strapi API."""
    server_config = _get_server_config(server_name)
    api_url = server_config.get("api_url")
    api_key = server_config.get("api_key")

    if not api_url or not api_key:
        raise ValueError(f"API URL or key is missing for server '{server_name}'")

    headers = {"Authorization": f"Bearer {api_key}"}
    if not files:
        headers["Content-Type"] = "application/json"

    # Handle list parameters for Strapi's query syntax
    processed_params = {}
    if params:
        for key, value in params.items():
            if isinstance(value, list):
                for i, item in enumerate(value):
                    processed_params[f"{key}[{i}]"] = item
            else:
                processed_params[key] = value

    try:
        response = requests.request(
            method,
            f"{api_url}{endpoint}",
            headers=headers,
            params=processed_params,
            json=json_body,
            files=files
        )
        response.raise_for_status()
        # Non-ASCII characters (like Japanese) must be handled correctly.
        return json.loads(response.text)
    except requests.exceptions.RequestException as e:
        # Try to parse error from Strapi's response
        try:
            error_details = e.response.json()
        except (AttributeError, json.JSONDecodeError):
            error_details = str(e)
        raise ConnectionError(f"API request to '{server_name}' failed: {error_details}")

# --- MCP Tools ---

@mcp.tool()
def greet(name: str) -> str:
    """指定された人物に挨拶を返します。"""
    return f"Hello, {name}!"

@mcp.tool()
def strapi_list_servers() -> str:
    """設定ファイルから利用可能なStrapiサーバーのリストを読み込みます。"""
    try:
        config = _load_config()
        servers = [
            {
                "name": name,
                "api_url": details.get("api_url"),
                "version": details.get("version", "N/A"),
            }
            for name, details in config.items()
        ]
        return json.dumps({"servers": servers}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
def strapi_get_content_types(server: str) -> str:
    """指定されたStrapiサーバーからコンテンツタイプのスキーマを取得します。"""
    try:
        data = _make_strapi_request(server, "/api/content-type-builder/content-types")
        
        # Add a helpful usage guide to the response
        usage_guide = {
            "naming_conventions": {
                "rest_api": "Use pluralName for REST API endpoints (e.g., 'api/articles' for pluralName: 'articles')",
                "graphql": {
                    "collections": "Use pluralName for collections (e.g., 'query { articles { data { id } } }')",
                    "single_items": "Use singularName for single items (e.g., 'query { article(id: 1) { data { id } } }')"
                }
            },
            "examples": {
                "rest": {
                    "collection": "GET /api/{pluralName}",
                    "single": "GET /api/{pluralName}/{id}",
                    "create": "POST /api/{pluralName}",
                    "update": "PUT /api/{pluralName}/{id}",
                    "delete": "DELETE /api/{pluralName}/{id}"
                }
            },
            "important_notes": [
                "Always check singularName and pluralName in the schema for correct endpoint/query names",
                "REST endpoints always start with 'api/'",
                "For updates, always fetch current data first and include ALL fields in the update"
            ]
        }
        
        response_payload = {
            "data": data,
            "usage_guide": usage_guide
        }
        
        return json.dumps(response_payload, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
def strapi_get_components(server: str, page: int = 1, pageSize: int = 25) -> str:
    """指定されたStrapiサーバーからコンポーネントを取得します。"""
    try:
        params = {"pagination[page]": page, "pagination[pageSize]": pageSize}
        data = _make_strapi_request(server, "/api/content-type-builder/components", params=params)
        
        # Add pagination info and a usage guide
        response_payload = {
            "data": data.get("data", []),
            "meta": data.get("meta", {}),
            "usage_guide": {
                "pagination": "Use 'page' and 'pageSize' parameters to navigate through results.",
                "next_steps": "Component schemas can be used to understand the structure of dynamic zones in your content types."
            }
        }
        return json.dumps(response_payload, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
def get_accel_articles(server: str, params: str = '{}') -> str:
    """
    Strapiから記事を取得します。APIのフィルタが不安定なため、全件取得してからPython側でフィルタリングします。
    この関数は常に公開済みと下書きの両方の記事を返します。

    Args:
        server (str): Strapiサーバー名。
        params (str): Strapi APIに渡す追加のクエリパラメータ（JSON形式）。sort, filters, paginationをサポートします。
    """
    try:
        params_dict = json.loads(params)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid params JSON format."})

    # Step 1: Fetch all articles (published and draft) from Strapi.
    # This project uses a custom 'status=draft' parameter to include drafts.
    fetch_params = {'pagination[pageSize]': 250, 'status': 'draft'}

    try:
        all_articles_data = _make_strapi_request(server, "/api/accel-articles", "GET", params=fetch_params)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch data from Strapi: {e}"})

    articles = all_articles_data.get('data', [])
    if not isinstance(articles, list):
        return json.dumps({"error": "Unexpected data format from Strapi", "data": all_articles_data})

    # Step 2: Apply user-defined filters from params.
    if 'filters' in params_dict:
        filters = params_dict['filters']
        for key, value in filters.items():
            if isinstance(value, dict):  # Handle operators like $eq, $contains
                op, filter_val = next(iter(value.items()))
                if op == '$eq':
                    articles = [a for a in articles if a.get('attributes', {}).get(key) == filter_val]
                elif op == '$contains':
                    articles = [a for a in articles if filter_val in a.get('attributes', {}).get(key, '')]
                elif op == '$null':
                    is_null = str(filter_val).lower() == 'true'
                    articles = [a for a in articles if (a.get('attributes', {}).get(key) is None) == is_null]
            else: # Handle direct equality
                articles = [a for a in articles if a.get('attributes', {}).get(key) == value]

    # Step 3: Apply sorting from params.
    if 'sort' in params_dict:
        sort_keys = params_dict['sort'].split(',')
        for sort_key in reversed(sort_keys): # Apply sorts in reverse order
            key, direction = (sort_key.split(':') + ['asc'])[:2]
            reverse = direction.lower() == 'desc'
            articles.sort(key=lambda x: x.get('attributes', {}).get(key, ''), reverse=reverse)

    # Step 4: Apply pagination from params.
    total = len(articles)
    page = int(params_dict.get('pagination[page]', 1))
    page_size = int(params_dict.get('pagination[limit]', 25))
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_articles = articles[start_index:end_index]

    result = {
        "data": paginated_articles,
        "meta": {
            "pagination": {
                "page": page,
                "pageSize": page_size,
                "pageCount": (total + page_size - 1) // page_size,
                "total": total
            }
        }
    }
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def create_accel_article_draft(server: str, body: str) -> str:
    """
    新しいAccel記事を下書きとして作成します。
    このツールはstrapi_restツール内の記事作成ロジックを独立させたもので、下書き処理を含め完全に同一の動作をします。
    """
    try:
        body_dict = json.loads(body)
        if 'data' not in body_dict:
            return json.dumps({"error": "Request body must contain a 'data' key."}, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid body JSON format."}, indent=2)

    provided_data = body_dict.get("data", {})

    # --- Pre-request Validation and Cleanup ---
    # 1. 自動的に 'body' を 'main_content' にリネーム
    if 'body' in provided_data and 'main_content' not in provided_data:
        provided_data['main_content'] = provided_data.pop('body')

    # 2. 必須フィールドの検証
    required_fields = ['title', 'slug', 'main_content']
    missing_fields = [field for field in required_fields if field not in provided_data or not provided_data[field]]
    if missing_fields:
        return json.dumps({
            "error": "Missing required fields in 'data'.",
            "message": f"Please provide the following fields: {', '.join(missing_fields)}."
        }, indent=2)

    endpoint = "/api/accel-articles"
    method = "POST"

    # 著者フィールドはオプションとして扱います。指定がない場合は著者なしで作成されます。

    # カテゴリの自動選択ロジック
    if 'accel_article_categories' not in provided_data:
        try:
            categories_response = _make_strapi_request(server, "/api/accel-article-categories", "GET", params={"fields": ["slug"], "pagination[pageSize]": 250})
            categories = categories_response.get("data", [])
            if categories:
                article_text = (
                    provided_data.get("title", "") + " " +
                    (provided_data.get("summary", "") or "") + " " +
                    (provided_data.get("main_content", "") or "")
                ).lower()
                
                selected_category_ids = []
                for cat in categories:
                    if cat.get('documentId'):
                        slug = cat.get('attributes', {}).get('slug', '')
                        normalized_slug = slug.replace('-', '').lower() if slug else ''
                        normalized_text = article_text.replace('-', '').replace(' ', '')
                        if slug and normalized_slug in normalized_text:
                            selected_category_ids.append(cat.get('documentId'))
                
                provided_data['accel_article_categories'] = selected_category_ids
        except Exception:
            # カテゴリの取得や処理に失敗しても、エラーにせず続行
            provided_data['accel_article_categories'] = []


    # タグの自動選択ロジック
    if 'accel_article_tags' not in provided_data:
        try:
            tags_response = _make_strapi_request(server, "/api/accel-article-tags", "GET", params={"fields": ["slug"], "pagination[pageSize]": 250})
            tags = tags_response.get("data", [])
            if tags:
                article_text = (
                    provided_data.get("title", "") + " " +
                    (provided_data.get("summary", "") or "") + " " +
                    (provided_data.get("main_content", "") or "")
                ).lower()
                
                selected_tag_ids = []
                for tag in tags:
                    if tag.get('documentId'):
                        slug = tag.get('attributes', {}).get('slug', '')
                        normalized_slug = slug.replace('-', '').lower() if slug else ''
                        normalized_text = article_text.replace('-', '').replace(' ', '')
                        if slug and normalized_slug in normalized_text:
                            selected_tag_ids.append(tag.get('documentId'))

                provided_data['accel_article_tags'] = selected_tag_ids
        except Exception:
            # タグの取得や処理に失敗しても、エラーにせず続行
            provided_data['accel_article_tags'] = []

    # 公開日の自動設定ロジック
    if 'publishedDate' not in provided_data:
        from datetime import datetime
        provided_data['publishedDate'] = datetime.now().strftime('%Y-%m-%d')
        body_dict['data'] = provided_data


    # 下書きとして投稿するロジック
    params_dict = {'status': 'draft'}
    # ユーザーの指示により、publishedDateが含まれていても削除しないように変更


    # --- APIリクエスト実行 ---
    try:
        data = _make_strapi_request(server, endpoint, method, params=params_dict, json_body=body_dict)

        response_payload = {
            "status": "success",
            "request": {"server": server, "endpoint": endpoint, "method": method},
            "response": data
        }

        # 3. 作成後のダイレクトリンク生成ロジック
        if data and isinstance(data.get("data"), dict) and ("id" in data["data"] or "documentId" in data["data"]):
            try:
                server_config = _get_server_config(server)
                admin_url = server_config.get("api_url")
                if admin_url:
                    entry_id = data["data"].get("documentId") or data["data"].get("id")
                    # このツールはaccel-article専用なのでUIDは固定
                    uid = "api::accel-article.accel-article"
                    direct_link = f"{admin_url.rstrip('/')}/admin/content-manager/collection-types/{uid}/{entry_id}"
                    response_payload["direct_link"] = direct_link
            except Exception:
                pass  # リンク生成に失敗してもサイレントに処理

        return json.dumps(response_payload, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def strapi_rest(server: str, endpoint: str, method: str = "GET", params: str = '{}', body: str = '{}', userAuthorized: bool = False, skip_field_check: bool = False) -> str:
    """Strapi APIに対してRESTリクエストを実行します。書き込み操作には userAuthorized=True が必須です。"""
    method = method.upper()
    if method in ["POST", "PUT", "DELETE"] and not userAuthorized:
        return json.dumps({"error": "AUTHORIZATION REQUIRED: This operation requires userAuthorized=True."}, indent=2)

    try:
        final_endpoint = endpoint
        params_dict = json.loads(params)
        body_dict = json.loads(body)

        if '?' in final_endpoint:
            base, query_string = final_endpoint.split('?', 1)
            final_endpoint = base
            # Correctly parse query string into a dict
            query_params = {}
            for p in query_string.split('&'):
                if '=' in p:
                    key, value = p.split('=', 1)
                    query_params[key] = value
            params_dict.update(query_params)

        is_accel_article_post = method == "POST" and "accel-articles" in final_endpoint and "content-manager" not in final_endpoint

        # Check for optional fields before posting
        if is_accel_article_post and not skip_field_check:
            try:
                content_types_data = _make_strapi_request(server, "/api/content-type-builder/content-types")
                accel_article_schema = next((ct for ct in content_types_data.get("data", []) if ct.get("uid") == "api::accel-article.accel-article"), None)
                
                if accel_article_schema:
                    attributes = accel_article_schema.get("schema", {}).get("attributes", {})
                    suggestible_fields = [
                        name for name, attr in attributes.items()
                        if attr.get("type") not in ["relation", "uid"] and not attr.get("required", False)
                    ]
                    provided_fields = list(body_dict.get("data", {}).keys())
                    missing_fields = [f for f in suggestible_fields if f not in provided_fields]
                    
                    if missing_fields:
                        return json.dumps({
                            "status": "clarification_needed",
                            "message": f"The 'Accel Article' has other optional fields: {', '.join(missing_fields)}. Do you want to add any of these? If not, say 'no' to proceed with the existing data.",
                            "how_to_proceed": "To proceed without adding fields, resend the request with the 'skip_field_check=True' parameter.",
                            "available_fields": missing_fields
                        }, indent=2)
            except Exception:
                pass 

        # For POST requests for accel-articles, add status=draft
        if is_accel_article_post:
            params_dict['status'] = 'draft'
            if body_dict and 'data' in body_dict and 'publishedDate' in body_dict.get('data', {}):
                del body_dict['data']['publishedDate']

        data = _make_strapi_request(server, final_endpoint, method, params=params_dict, json_body=body_dict)

        response_payload = {
            "status": "success",
            "request": {"server": server, "endpoint": final_endpoint, "method": method},
            "response": data
        }

        # Add direct admin link for successful POST creations
        if method == "POST" and data and isinstance(data.get("data"), dict) and ("id" in data["data"] or "documentId" in data["data"]):
            try:
                server_config = _get_server_config(server)
                admin_url = server_config.get("api_url")
                if admin_url:
                    entry_id = data["data"].get("documentId") or data["data"].get("id")
                    plural_name = final_endpoint.split('?')[0].split('/')[-1]
                    
                    content_types_data = _make_strapi_request(server, "/api/content-type-builder/content-types")
                    content_type_schema = next(
                        (ct for ct in content_types_data.get("data", []) if ct.get("schema", {}).get("pluralName") == plural_name), 
                        None
                    )
                    
                    if content_type_schema:
                        uid = content_type_schema.get("uid")
                        direct_link = f"{admin_url.rstrip('/')}/admin/content-manager/collection-types/{uid}/{entry_id}"
                        response_payload["direct_link"] = direct_link
            except Exception:
                pass  # Fail silently if link generation fails

        return json.dumps(response_payload, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
def strapi_upload_media(server: str, url: str, format: str = "original", quality: int = 80, metadata: str = '{}', userAuthorized: bool = False) -> str:
    """URLから画像をダウンロードし、Strapiにアップロードします。userAuthorized=True が必須です。"""
    if not userAuthorized:
        return json.dumps({"error": "AUTHORIZATION REQUIRED: Media upload requires userAuthorized=True."}, indent=2)
    
    try:
        # (Download and process image logic remains the same)
        response = requests.get(url, stream=True)
        response.raise_for_status()
        image = Image.open(response.raw)
        output_buffer = io.BytesIO()
        file_format = image.format.lower() if format == "original" else format
        if file_format == "jpeg":
            image.save(output_buffer, format="JPEG", quality=quality)
        elif file_format == "png":
            image.save(output_buffer, format="PNG")
        elif file_format == "webp":
            image.save(output_buffer, format="WEBP", quality=quality)
        else:
            image.save(output_buffer, format=image.format)
        output_buffer.seek(0)
        
        parsed_url = urlparse(url)
        original_filename = Path(parsed_url.path).name
        filename = f"{Path(original_filename).stem}.{file_format.lower()}"
        mime_type = mimetypes.guess_type(filename)[0] or f"image/{file_format.lower()}"
        files = {'files': (filename, output_buffer, mime_type)}
        
        metadata_dict = json.loads(metadata)
        if metadata_dict:
            files['fileInfo'] = (None, json.dumps(metadata_dict), 'application/json')
            
        # Upload to Strapi
        upload_response = _make_strapi_request(server, "/api/upload", "POST", files=files)
        
        # Create a helpful response
        if not upload_response or not isinstance(upload_response, list) or not upload_response[0].get('id'):
             raise ValueError("Upload failed or returned an unexpected format.")

        uploaded_file = upload_response[0]
        file_id = uploaded_file.get("id")
        file_url = uploaded_file.get("url")

        response_payload = {
            "status": "success",
            "uploaded_file": {
                "id": file_id,
                "name": uploaded_file.get("name"),
                "url": file_url,
                "mime": uploaded_file.get("mime"),
                "size_kb": round(uploaded_file.get("size", 0), 2)
            },
            "how_to_use": {
                "guide": "To link this media to a content type, use the `strapi_rest` tool.",
                "example": {
                    "tool": "strapi_rest",
                    "server": server,
                    "method": "PUT",
                    "endpoint": "/api/{pluralName}/{entry_id}",
                    "body": f"{{ \"data\": {{ \"your_media_field_name\": {file_id} }} }}",
                    "userAuthorized": True
                }
            }
        }
        return json.dumps(response_payload, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

def main():
    """Package entry point."""
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()