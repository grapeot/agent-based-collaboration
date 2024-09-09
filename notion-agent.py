import os
from dotenv import load_dotenv
import requests
from notion_client import Client
import re

# Load environment variables
load_dotenv()

# Set up Notion client
notion = Client(auth=os.getenv("NOTION_API_KEY"))

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def update_notion_page(page_id, content):
    # Split content into paragraphs
    paragraphs = content.split('\n\n')
    
    for paragraph in paragraphs:
        # If a single paragraph is longer than 2000 characters, split it
        if len(paragraph) > 2000:
            chunks = [paragraph[i:i+2000] for i in range(0, len(paragraph), 2000)]
            for chunk in chunks:
                notion.blocks.children.append(
                    block_id=page_id,
                    children=[
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": chunk.strip()}}]
                            }
                        }
                    ]
                )
        else:
            notion.blocks.children.append(
                block_id=page_id,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": paragraph.strip()}}]
                        }
                    }
                ]
            )

# Main execution
file_path = "transcript.txt"
page_id = os.getenv("NOTION_PAGE_ID")

# Read the content from the file
file_content = read_file(file_path)

# Clear existing content (optional)
notion.blocks.children.list(block_id=page_id)
for block in notion.blocks.children.list(block_id=page_id)["results"]:
    notion.blocks.delete(block_id=block["id"])

# Update the Notion page with new content
update_notion_page(page_id, file_content)

print("Content updated successfully!")