from typing import Annotated

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Google

from arcade_google_docs.utils import build_drive_service


@tool(
    requires_auth=Google(
        scopes=[
            "https://www.googleapis.com/auth/drive.file",
        ],
    )
)
async def comment_on_document(
    context: ToolContext,
    document_id: Annotated[str, "The ID of the document to comment on"],
    comment_text: Annotated[str, "The comment to add to the document"],
) -> Annotated[dict, "The comment's ID, documentId, and documentUrl in a dictionary"]:
    """
    Comment on a specific document by its ID.
    """
    drive_service = build_drive_service(context.get_auth_token_or_empty())

    response = (
        drive_service.comments()
        .create(
            fileId=document_id,
            body={
                "content": comment_text,
            },
            fields="id",
        )
        .execute()
    )

    return {
        "comment_id": response["id"],
        "document_url": f"https://docs.google.com/document/d/{document_id}",
    }


@tool(
    requires_auth=Google(
        scopes=[
            "https://www.googleapis.com/auth/drive.file",
        ],
    )
)
async def list_document_comments(
    context: ToolContext,
    document_id: Annotated[str, "The ID of the document to list comments for"],
    include_deleted: Annotated[
        bool,
        "Whether to include deleted comments in the results. Defaults to False.",
    ] = False,
) -> Annotated[
    dict,
    "A dictionary containing the comments",
]:
    """
    List all comments on the specified Google Docs document.
    """
    drive_service = build_drive_service(context.get_auth_token_or_empty())

    comments: list[dict] = []
    params: dict = {
        "fileId": document_id,
        "pageSize": 100,
        "fields": (
            "nextPageToken,comments(id,content,createdTime,modifiedTime,deleted,"
            "author(displayName,emailAddress),replies(id,content,createdTime,modifiedTime,deleted,author(displayName,emailAddress)))"
        ),
    }
    if include_deleted:
        params["includeDeleted"] = True

    while True:
        results = drive_service.comments().list(**params).execute()
        batch = results.get("comments", [])
        comments.extend(batch)
        next_page_token = results.get("nextPageToken")
        if not next_page_token:
            break
        params["pageToken"] = next_page_token

    reply_count = 0
    for comment in comments:
        reply_count += len(comment.get("replies", []))

    return {
        "comments_count": len(comments),
        "replies_count": reply_count,
        "total_discussion_count": len(comments) + reply_count,
        "comments": comments,
        "document_url": f"https://docs.google.com/document/d/{document_id}",
    }
