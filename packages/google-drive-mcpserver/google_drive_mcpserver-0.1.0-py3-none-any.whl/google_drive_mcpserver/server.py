import os
from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import List, Optional, Annotated
from pydantic import Field
from googleapiclient.http import MediaIoBaseDownload
import io

mcp = FastMCP("netmind-mcpserver-mcp")

creds = Credentials(
    token=os.environ["GOOGLE_ACCESS_TOKEN"],
    refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ["GOOGLE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    scopes=[
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.photos.readonly",
        "https://www.googleapis.com/auth/drive.appdata"
    ]
)
service = build("drive", "v3", credentials=creds)


@mcp.tool(description="Search for files in Google Drive.")
async def list_file(
        orderBy: Annotated[
            Optional[str],
            Field(
                description=(
                        "A comma-separated list of sort keys. Valid keys are 'createdTime', 'folder', 'modifiedByMeTime', "
                        "'modifiedTime', 'name', 'name_natural', 'quotaBytesUsed', 'recency', 'sharedWithMeTime', 'starred', "
                        "and 'viewedByMeTime'. Each key sorts ascending by default, but may be reversed with the 'desc' modifier.")
            )
        ] = None,
        pageSize: Annotated[
            Optional[int],
            Field(
                description=(
                        "The maximum number of files to return per page. Partial or empty result pages are possible even "
                        "before the end of the files list has been reached.")
            )
        ] = None,
        query: Annotated[
            Optional[str],
            Field(
                description=(
                        "Search query")
            )
        ] = None,
        pageToken: Annotated[
            Optional[str],
            Field(
                description=("The token for continuing a previous list request on the next page. "
                             "This should be set to the value of 'nextPageToken' from the previous response.")
            )
        ] = None
) -> List[dict]:
    params = {
        "orderBy": orderBy,
        "pageSize": pageSize,
        "pageToken": pageToken,
        "fields": "nextPageToken, files(id, name, mimeType, modifiedTime, size, webViewLink)"
    }
    if query:
        escaped_query = query.replace("\\", "\\\\").replace("'", "\\'")
        params["q"] = f"fullText contains '{escaped_query}'"

    params = {k: v for k, v in params.items() if v is not None}
    results = service.files().list(**params).execute()
    files = results.get("files", [])

    return files


@mcp.tool(description="Permanently delete a file from Google Drive.")
async def delete_file(
        fileId: Annotated[
            str,
            Field(description="The ID of the file to delete. Required.")
        ]
) -> dict:
    """Delete a file in Google Drive permanently (not moved to trash)."""

    params = {
        "fileId": fileId,
    }
    params = {k: v for k, v in params.items() if v is not None}
    try:
        service.files().delete(**params).execute()
        return {"status": "success", "fileId": fileId}
    except Exception as e:
        return {"status": "error", "fileId": fileId, "message": str(e)}


@mcp.tool(description="Read contents of a file from Google Drive")
async def get_file(
        fileId: Annotated[
            str,
            Field(description="The ID of the file to retrieve. Required.")
        ]
) -> dict:
    params = {
        "fileId": fileId,
    }
    params = {k: v for k, v in params.items() if v is not None}

    try:

        file = service.files().get(
            fileId=fileId, fields="id, name, mimeType"
        ).execute()
        mime_type = file.get("mimeType", "application/octet-stream")
        name = file.get("name", fileId)

        if mime_type.startswith("application/vnd.google-apps"):
            export_map = {
                "application/vnd.google-apps.document": "text/markdown",
                "application/vnd.google-apps.spreadsheet": "text/csv",
                "application/vnd.google-apps.presentation": "text/plain",
                "application/vnd.google-apps.drawing": "image/png",
            }
            export_mime_type = export_map.get(mime_type, "text/plain")

            res = service.files().export(fileId=fileId, mimeType=export_mime_type).execute()

            return {
                "status": "success",
                "id": fileId,
                "name": name,
                "text": res if isinstance(res, str) else res.decode("utf-8", errors="ignore"),

            }

        request = service.files().get_media(**params)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        fh.seek(0)
        content = fh.read()
        return {
            "status": "success",
            "id": fileId,
            "name": name,
            "content": content.decode("utf-8", errors="ignore")
        }

    except Exception as e:
        return {"status": "error", "fileId": fileId, "message": str(e)}


def main():
    mcp.run()


if __name__ == '__main__':
    main()
