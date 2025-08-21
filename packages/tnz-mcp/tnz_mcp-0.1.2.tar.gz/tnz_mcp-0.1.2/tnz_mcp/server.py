import os
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime

from tnzapi import TNZAPI
from mcp.server.fastmcp import FastMCP
from .config import load_config

def run_server(transport: str = "stdio", host: Optional[str] = None, port: Optional[int] = None) -> None:
    """Run the TNZ MCP server with specified transport (stdio or streamable-http)."""
    try:
        # Validate transport
        if transport not in ["stdio", "streamable-http"]:
            raise ValueError("Transport must be 'stdio' or 'streamable-http'")
        
        # For streamable-http, ensure host and port are provided
        if transport == "streamable-http" and (not host or not port):
            raise ValueError("Host and port must be specified for streamable-http transport")

        # Load configuration
        config = load_config()
        auth_token = config.get("auth_token")
        if not auth_token:
            raise ValueError("TNZ_AUTH_TOKEN must be set in environment or config file")

        client = TNZAPI(AuthToken=auth_token)
        mcp = FastMCP("TNZ Messaging and Addressbook API")

        # Messaging Tools
        @mcp.tool()
        def send_sms(reference: str, message_text: str, recipients: List[str]) -> Dict[str, Any]:
            """Send an SMS message to one or more recipients."""
            try:
                response = client.Messaging.SMS.SendMessage(
                    Reference=reference,
                    MessageText=message_text,
                    Recipients=recipients
                )
                return response.__dict__  # Convert to dict for serialization
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def send_email(subject: str, recipients: List[str], message_plain: str, message_html: Optional[str] = None) -> Dict[str, Any]:
            """Send an Email to one or more recipients. Optionally include HTML content."""
            try:
                params = {
                    "EmailSubject": subject,
                    "Recipients": recipients,
                    "MessagePlain": message_plain
                }
                if message_html:
                    params["MessageHTML"] = message_html
                response = client.Messaging.Email.SendMessage(**params)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def send_fax(recipients: List[str], attachments: List[str]) -> Dict[str, Any]:
            """Send a Fax document to one or more recipients. Attachments are local file paths."""
            try:
                response = client.Messaging.Fax.SendMessage(
                    Recipients=recipients,
                    Attachments=attachments
                )
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def send_tts(recipient: str, reference: str, message_to_people: str, keypads: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
            """Make a Text-to-Speech (TTS) call. Keypads are optional for interactive responses."""
            try:
                from tnzapi.api.messaging.dtos.keypad import Keypad
                keypad_objs = [Keypad(**kp) for kp in keypads] if keypads else []
                response = client.Messaging.TTS.SendMessage(
                    Recipients=[recipient],
                    Reference=reference,
                    MessageToPeople=message_to_people,
                    Keypads=keypad_objs
                )
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def send_voice(recipient: str, reference: str, message_to_people: str, message_to_answer_phones: Optional[str] = None, keypads: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
            """Make a Voice call with uploaded audio files. Keypads are optional."""
            try:
                from tnzapi.api.messaging.dtos.keypad import Keypad
                keypad_objs = [Keypad(**kp) for kp in keypads] if keypads else []
                params = {
                    "Recipients": [recipient],
                    "Reference": reference,
                    "MessageToPeople": message_to_people
                }
                if message_to_answer_phones:
                    params["MessageToAnswerPhones"] = message_to_answer_phones
                response = client.Messaging.Voice.SendMessage(**params, Keypads=keypad_objs)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        # Reports Tools
        @mcp.tool()
        def get_message_status(message_id: str) -> Dict[str, Any]:
            """Get the status of a sent message. Please repond the message status from Recipients.Status instead of main Status """
            try:
                response = client.Reports.Status.Poll(MessageID=message_id)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def get_sms_reply(message_id: str) -> Dict[str, Any]:
            """Get SMS replies for a message."""
            try:
                response = client.Reports.SMSReply.Poll(MessageID=message_id)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def get_sms_received(date_from: str, date_to: str) -> Dict[str, Any]:
            """Get list of received SMS messages in a date range (format: YYYY-MM-DD HH:MM:SS)."""
            try:
                response = client.Reports.SMSReceived.Poll(DateFrom=date_from, DateTo=date_to)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        # Actions Tools
        @mcp.tool()
        def abort_job(message_id: str) -> Dict[str, Any]:
            """Abort a pending or delayed job."""
            try:
                response = client.Actions.Abort.SendRequest(MessageID=message_id)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def resubmit_job(message_id: str, send_time: Optional[str] = None) -> Dict[str, Any]:
            """Resubmit a failed job. SendTime is optional (format: YYYY-MM-DDTHH:MM)."""
            try:
                params = {"MessageID": message_id}
                if send_time:
                    params["SendTime"] = send_time
                response = client.Actions.Resubmit.SendRequest(**params)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def reschedule_job(message_id: str, send_time: str) -> Dict[str, Any]:
            """Reschedule a delayed job (SendTime format: YYYY-MM-DDTHH:MM)."""
            try:
                response = client.Actions.Reschedule.SendRequest(
                    MessageID=message_id,
                    SendTime=datetime.fromisoformat(send_time)
                )
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def set_pacing(message_id: str, number_of_operators: int) -> Dict[str, Any]:
            """Set the number of operators for a TTS/Voice job."""
            try:
                response = client.Actions.Pacing.SendRequest(
                    MessageID=message_id,
                    NumberOfOperators=number_of_operators
                )
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        # Addressbook - Contacts Tools
        @mcp.tool()
        def find_contacts(attention: str, first_name:str, last_name:str, mobile_number:str, email_address:str, phone_number:str, records_per_page: int = 10, page: int = 1) -> Dict[str, Any]:
            """
            Find / search contacts with pagination.

            You can find contacts using at least 1 property from the below:
            - attention
            - first_name
            - last_name
            - mobile_number
            - email_address
            """
            try:
                response = client.Addressbook.Contact.Search(
                    Attention=attention,
                    FirstName=first_name,
                    LastName=last_name,
                    MobilePhone=mobile_number, 
                    EmailAddress=email_address,
                    MainPhone=phone_number,
                    RecordsPerPage=records_per_page,
                    Page=page
                )

                return response.__dict__
            except Exception as e:
                return {"error": str(e)}
                
        @mcp.tool()
        def list_contacts(records_per_page: int = 10, page: int = 1) -> Dict[str, Any]:
            """List contacts with pagination."""
            try:
                response = client.Addressbook.Contact.List(RecordsPerPage=records_per_page, Page=page)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def get_contact_detail(contact_id: str) -> Dict[str, Any]:
            """Get details of a contact."""
            try:
                response = client.Addressbook.Contact.Detail(ContactID=contact_id)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def create_contact(title: Optional[str] = None, company: Optional[str] = None, first_name: str = "", last_name: str = "", mobile_phone: Optional[str] = None, view_public: str = "Account", edit_public: str = "Account") -> Dict[str, Any]:
            """Create a new contact."""
            try:
                response = client.Addressbook.Contact.Create(
                    Title=title,
                    Company=company,
                    FirstName=first_name,
                    LastName=last_name,
                    MobilePhone=mobile_phone,
                    ViewPublic=view_public,
                    EditPublic=edit_public
                )
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def update_contact(contact_id: str, **updates: Dict[str, Any]) -> Dict[str, Any]:
            """Update a contact. Provide fields to update as kwargs (e.g., Attention='New Attention')."""
            try:
                response = client.Addressbook.Contact.Update(ContactID=contact_id, **updates)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def delete_contact(contact_id: str) -> Dict[str, Any]:
            """Delete a contact."""
            try:
                response = client.Addressbook.Contact.Delete(ContactID=contact_id)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        # Addressbook - Groups
        @mcp.tool()
        def create_group(group_code: str, group_name: str) -> Dict[str, Any]:
            """Create a new group."""
            try:
                response = client.Addressbook.Group.Create(GroupCode=group_code, GroupName=group_name)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def list_groups(records_per_page: int = 10, page: int = 1) -> Dict[str, Any]:
            """List groups with pagination."""
            try:
                response = client.Addressbook.Group.List(RecordsPerPage=records_per_page, Page=page)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def get_group_detail(group_code: str) -> Dict[str, Any]:
            """Get details of a group."""
            try:
                response = client.Addressbook.Group.Detail(GroupCode=group_code)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def update_group(group_code: str, group_name: str) -> Dict[str, Any]:
            """Update a group."""
            try:
                response = client.Addressbook.Group.Update(GroupCode=group_code, GroupName=group_name)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def delete_group(group_code: str) -> Dict[str, Any]:
            """Delete a group."""
            try:
                response = client.Addressbook.Group.Delete(GroupCode=group_code)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        # Addressbook - Contact Groups
        @mcp.tool()
        def list_contact_groups(records_per_page: int = 10, page: int = 1, contact_id: Optional[str] = None) -> Dict[str, Any]:
            """List contact groups with pagination, optionally filtered by contact_id."""
            try:
                params = {"RecordsPerPage": records_per_page, "Page": page}
                if contact_id:
                    params["ContactID"] = contact_id
                response = client.Addressbook.ContactGroup.List(**params)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def get_contact_group_detail(contact_id: str, group_code: str) -> Dict[str, Any]:
            """Get details of a contact group relationship."""
            try:
                response = client.Addressbook.ContactGroup.Detail(ContactID=contact_id, GroupCode=group_code)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def create_contact_group(contact_id: str, group_code: str) -> Dict[str, Any]:
            """Create a contact group relationship."""
            try:
                response = client.Addressbook.ContactGroup.Create(ContactID=contact_id, GroupCode=group_code)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def delete_contact_group(contact_id: str, group_code: str) -> Dict[str, Any]:
            """Delete a contact group relationship."""
            try:
                response = client.Addressbook.ContactGroup.Delete(ContactID=contact_id, GroupCode=group_code)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        # Addressbook - Group Contacts
        @mcp.tool()
        def list_group_contacts(records_per_page: int = 10, page: int = 1, group_code: Optional[str] = None) -> Dict[str, Any]:
            """List group contacts with pagination, optionally filtered by group_code."""
            try:
                params = {"RecordsPerPage": records_per_page, "Page": page}
                if group_code:
                    params["GroupCode"] = group_code
                response = client.Addressbook.GroupContact.List(**params)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def get_group_contact_detail(group_code: str, contact_id: str) -> Dict[str, Any]:
            """Get details of a group contact relationship."""
            try:
                response = client.Addressbook.GroupContact.Detail(GroupCode=group_code, ContactID=contact_id)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def create_group_contact(group_code: str, contact_id: str) -> Dict[str, Any]:
            """Create a group contact relationship."""
            try:
                response = client.Addressbook.GroupContact.Create(GroupCode=group_code, ContactID=contact_id)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        def delete_group_contact(group_code: str, contact_id: str) -> Dict[str, Any]:
            """Delete a group contact relationship."""
            try:
                response = client.Addressbook.GroupContact.Delete(GroupCode=group_code, ContactID=contact_id)
                return response.__dict__
            except Exception as e:
                return {"error": str(e)}

        # Resource
        @mcp.resource("messages://status/{message_id}")
        def get_message_status_resource(message_id: str) -> str:
            """Resource for message status."""
            try:
                response = client.Reports.Status.Poll(MessageID=message_id)
                return str(response)
            except Exception as e:
                return f"Error: {str(e)}"

        # Prompt
        @mcp.prompt()
        def generate_message_prompt(message: str, tone: str = "friendly") -> str:
            """Generate a message response in a specific tone."""
            tones = {
                "friendly": "Write a warm, friendly message",
                "formal": "Write a formal, professional message",
                "casual": "Write a casual, relaxed message",
            }
            return f"{tones.get(tone, tones['friendly'])} based on: {message}."

        # Start the server
        if transport == "stdio":
            print("Starting TNZ MCP server on stdio")
            mcp.run(transport="stdio")
        else:
            print(f"Starting TNZ MCP server on {host}:{port} with {transport}")
            mcp.run(transport=transport, host=host, port=port)

    except Exception as e:
        print(f"Failed to start server: {str(e)}")
        raise

def main():
    """CLI entry point for running the TNZ MCP server."""
    parser = argparse.ArgumentParser(description="TNZ MCP Server for Claude Desktop and Gemini CLI")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "streamable-http"], help="Transport protocol (default: stdio)")
    parser.add_argument("--host", default=None, help="Host to run the server on (required for streamable-http)")
    parser.add_argument("--port", type=int, default=None, help="Port to run the server on (required for streamable-http)")
    args = parser.parse_args()
    run_server(transport=args.transport, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
