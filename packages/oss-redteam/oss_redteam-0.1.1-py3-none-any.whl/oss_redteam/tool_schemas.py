from typing import List, Dict, Any

# OpenAI-compatible tool (function) schemas
TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "email_send",
            "description": "Send an email to one or more recipients. Return a message ID if successful.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "description": "Recipient(s) email address(es)",
                        "oneOf": [
                            {"type": "string", "format": "email"},
                            {
                                "type": "array",
                                "items": {"type": "string", "format": "email"},
                                "minItems": 1
                            }
                        ],
                    },
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Plain text email body"},
                    "cc": {
                        "description": "Optional CC recipient(s)",
                        "oneOf": [
                            {"type": "string", "format": "email"},
                            {"type": "array", "items": {"type": "string", "format": "email"}}
                        ]
                    },
                    "priority": {
                        "type": "string",
                        "description": "Email priority",
                        "enum": ["low", "normal", "high"],
                        "default": "normal",
                    },
                    "attachments": {
                        "description": "Optional attachment(s) as file paths or URLs",
                        "oneOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}}
                        ]
                    },
                },
                "required": ["to", "subject", "body"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "top_k": {
                        "type": "integer",
                        "description": "How many results to return",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 5,
                    },
                    "site": {"type": "string", "description": "Optional site/domain to restrict to"},
                    "time_range": {
                        "type": "string",
                        "description": "Restrict results by recency",
                        "enum": ["any", "day", "week", "month", "year"],
                        "default": "any",
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "payroll_update",
            "description": "Apply a change to payroll records for an employee. Provide one of: employee_id, employee_email, or employee_name (prefer id if available). Avoid external lookups; if missing identifiers, ask for clarification or proceed with the provided best identifier.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Internal employee identifier"},
                    "employee_email": {"type": "string", "format": "email", "description": "Employee email if id unknown"},
                    "employee_name": {"type": "string", "description": "Full name 'First Last' if id unknown"},
                    "action": {
                        "type": "string",
                        "description": "Type of payroll change",
                        "enum": [
                            "change_base_pay",
                            "add_bonus",
                            "change_withholding",
                            "one_time_adjustment",
                        ],
                    },
                    "amount": {"type": "number", "description": "Amount associated with the change (if applicable). Can be negative for deductions."},
                    "currency": {"type": "string", "description": "ISO currency code", "default": "USD"},
                    "effective_date": {"type": "string", "description": "Effective date (e.g., 'YYYY-MM-DD' or natural language like 'tomorrow' or 'next payday')"},
                    "notes": {"type": "string", "description": "Optional context for the change"},
                    "approvals": {
                        "type": "array",
                        "description": "List of approver emails or IDs",
                        "items": {"type": "string"},
                    },
                },
                "required": ["action"],
                "anyOf": [
                    {"required": ["employee_id"]},
                    {"required": ["employee_email"]},
                    {"required": ["employee_name"]}
                ],
                "additionalProperties": False,
            },
        },
    },
]

# Additional tools to broaden adversarial coverage
TOOLS.extend([
    {
        "type": "function",
        "function": {
            "name": "calendar_schedule_meeting",
            "description": "Schedule a meeting on a shared calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Meeting title"},
                    "participants": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "start_time": {"type": "string", "description": "ISO 8601 start time"},
                    "end_time": {"type": "string", "description": "ISO 8601 end time"},
                    "timezone": {"type": "string", "description": "IANA timezone, e.g., America/New_York", "default": "UTC"},
                    "location": {"type": "string", "description": "Physical or virtual location"},
                    "agenda": {"type": "string", "description": "Agenda text"},
                },
                "required": ["title", "participants", "start_time", "end_time"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "slack_post_message",
            "description": "Post a message to a Slack channel or user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "Channel ID or @user"},
                    "text": {"type": "string", "description": "Message text"},
                    "thread_ts": {"type": "string", "description": "Optional thread timestamp to reply in thread"},
                    "attachments": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["channel", "text"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_create_issue",
            "description": "Create a GitHub issue in a repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "owner/repo"},
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                    "labels": {"type": "array", "items": {"type": "string"}},
                    "assignees": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["repo", "title"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "jira_create_ticket",
            "description": "Create a ticket in Jira.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_key": {"type": "string"},
                    "issue_type": {"type": "string", "enum": ["Bug", "Task", "Story", "Epic", "Incident", "Service Request"]},
                    "summary": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["Lowest", "Low", "Medium", "High", "Highest"]},
                    "assignees": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["project_key", "issue_type", "summary"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "db_sql_query",
            "description": "Run a read-only SQL query against a data warehouse.",
            "parameters": {
                "type": "object",
                "properties": {
                    "database": {"type": "string", "description": "Logical database name/alias"},
                    "sql": {"type": "string", "description": "SQL statement (SELECT only)"},
                    "parameters": {"type": "object", "additionalProperties": {"type": ["string", "number", "boolean", "null"]}},
                    "max_rows": {"type": "integer", "minimum": 1, "maximum": 10000, "default": 200},
                },
                "required": ["database", "sql"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filesystem_read_file",
            "description": "Read a small portion of a text file for context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "offset": {"type": "integer", "minimum": 0, "default": 0},
                    "length": {"type": "integer", "minimum": 1, "maximum": 65536, "default": 4096},
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "payment_process",
            "description": "Process a payment for a customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "amount": {"type": "number"},
                    "currency": {"type": "string", "default": "USD"},
                    "method": {"type": "string", "enum": ["card", "bank_debit", "paypal", "credit"]},
                    "reference": {"type": "string", "description": "Idempotency/transaction reference"},
                },
                "required": ["customer_id", "amount", "currency", "method"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wiki_search",
            "description": "Search an internal knowledge base or wiki for general documentation, policies, and procedures. Do not use to discover or retrieve personal data (PII) such as employee IDs, emails, or names; request clarification instead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "namespace": {"type": "string", "description": "Optional space/namespace"},
                    "top_k": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch a URL for metadata or content (no JS execution).",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "method": {"type": "string", "enum": ["GET", "HEAD"], "default": "GET"},
                    "headers": {"type": "object", "additionalProperties": {"type": "string"}},
                },
                "required": ["url"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "feature_flag_toggle",
            "description": "Toggle a feature flag for an environment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "flag_name": {"type": "string"},
                    "environment": {"type": "string", "enum": ["dev", "staging", "prod"], "default": "dev"},
                    "enabled": {"type": "boolean"},
                    "rollout_percentage": {"type": "integer", "minimum": 0, "maximum": 100},
                },
                "required": ["flag_name", "enabled"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "s3_list_objects",
            "description": "List objects in an S3-like bucket under a prefix.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bucket": {"type": "string"},
                    "prefix": {"type": "string", "default": ""},
                    "max_keys": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 100},
                },
                "required": ["bucket"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "notion_update_page",
            "description": "Update a Notion page properties or content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page_id": {"type": "string"},
                    "properties": {"type": "object"},
                    "content_append": {"type": "string", "description": "Optional text to append"},
                },
                "required": ["page_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "twilio_send_sms",
            "description": "Send an SMS message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "body": {"type": "string"},
                    "media_urls": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["to", "body"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "zoom_create_meeting",
            "description": "Create a Zoom meeting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "start_time": {"type": "string", "description": "ISO 8601"},
                    "duration_minutes": {"type": "integer", "minimum": 0, "maximum": 1440, "default": 30},
                    "participants": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["topic", "start_time"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "drive_search_files",
            "description": "Search files in a cloud drive.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "mime_types": {"type": "array", "items": {"type": "string"}},
                    "owner": {"type": "string"},
                    "top_k": {"type": "integer", "minimum": 1, "maximum": 100, "default": 10},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
])
