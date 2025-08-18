"""
Enhanced Admin Interface for Unified LLM
Provides comprehensive admin dashboard and request history management.
"""

import json
import csv
import io
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi.responses import StreamingResponse

from ..utils.database import LLMDatabase


class AdminInterface:
    """Enhanced admin interface with improved features"""

    def __init__(self, db: LLMDatabase):
        self.db = db

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics"""
        try:
            base_stats = self.db.get_stats()

            # Add more detailed statistics
            now = datetime.now()

            # Last 7 days activity
            week_ago = now - timedelta(days=7)
            week_calls = len(self.db.get_calls(start_date=week_ago, limit=10000))  # Large limit to count all

            # Last hour activity
            hour_ago = now - timedelta(hours=1)
            hour_calls = len(self.db.get_calls(start_date=hour_ago, limit=10000))

            # Search usage statistics
            search_stats = {}
            all_calls = self.db.get_calls(limit=10000)  # Get all for analysis

            for call in all_calls:
                search_type = call.get("search_type", "none") or "none"
                search_stats[search_type] = search_stats.get(search_type, 0) + 1

            # Average response time
            durations = [call["duration_ms"] for call in all_calls if call.get("duration_ms")]
            avg_duration = sum(durations) / len(durations) if durations else 0

            # Token usage statistics
            total_tokens = 0
            token_count = 0
            for call in all_calls:
                if call.get("token_usage") and isinstance(call["token_usage"], dict):
                    tokens = call["token_usage"].get("total_tokens", 0)
                    if tokens:
                        total_tokens += tokens
                        token_count += 1

            avg_tokens = total_tokens / token_count if token_count > 0 else 0

            return {
                **base_stats,
                "week_calls": week_calls,
                "hour_calls": hour_calls,
                "search_stats": search_stats,
                "avg_duration_ms": round(avg_duration, 2),
                "total_tokens_used": total_tokens,
                "avg_tokens_per_call": round(avg_tokens, 2),
            }

        except Exception as e:
            # Return basic stats if detailed analysis fails
            return self.db.get_stats()

    def generate_dashboard_html(self) -> str:
        """Generate enhanced dashboard HTML using Tailwind template"""
        from fastapi.templating import Jinja2Templates
        from pathlib import Path

        # Setup templates
        templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

        # Add number_format filter
        def number_format(value):
            """Format numbers with commas"""
            if value is None:
                return "0"
            try:
                return f"{int(value):,}"
            except (ValueError, TypeError):
                return str(value)

        templates.env.filters["number_format"] = number_format

        # Get dashboard stats
        stats = self.get_dashboard_stats()

        # Prepare data for template
        provider_stats = stats.get("provider_stats", {})
        max_provider_count = max(provider_stats.values()) if provider_stats else 1

        model_stats = stats.get("model_stats", {})
        top_models = sorted(model_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        max_model_count = max([count for _, count in top_models]) if top_models else 1

        # Model display names mapping
        model_display_names = {
            "claude-sonnet-4-20250514": "Claude Sonnet 4",
            "gpt-4o-mini": "GPT-4o Mini",
            "gpt-4o": "GPT-4o",
            "gemini-1.5-flash-latest": "Gemini 1.5 Flash",
            "gemini-1.5-pro-latest": "Gemini 1.5 Pro",
        }

        # Calculate search requests count
        search_stats = stats.get("search_stats", {})
        search_requests_count = sum(search_stats.values()) - search_stats.get("none", 0)

        # Render template

        # Create a mock request object for template rendering
        class MockRequest:
            def __init__(self):
                self.url = type("obj", (object,), {"path": "/admin"})()

        request = MockRequest()

        template_response = templates.TemplateResponse(
            "admin_dashboard.html",
            {
                "request": request,
                "stats": stats,
                "provider_stats": provider_stats,
                "max_provider_count": max_provider_count,
                "top_models": top_models,
                "max_model_count": max_model_count,
                "model_display_names": model_display_names,
                "search_requests_count": search_requests_count,
            },
        )

        return template_response.body.decode("utf-8")

    def export_to_csv(self, limit: int = 1000) -> StreamingResponse:
        """Export LLM calls to CSV format"""
        calls = self.db.get_calls(limit=limit)

        def generate_csv():
            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(
                [
                    "ID",
                    "Timestamp",
                    "Model",
                    "Provider",
                    "Search Type",
                    "Prompt",
                    "Response",
                    "Duration (ms)",
                    "Total Tokens",
                    "Prompt Tokens",
                    "Completion Tokens",
                    "Error",
                ]
            )

            for call in calls:
                token_usage = call.get("token_usage") or {}
                writer.writerow(
                    [
                        call.get("id", ""),
                        call.get("timestamp", ""),
                        call.get("model", ""),
                        call.get("provider", ""),
                        call.get("search_type", ""),
                        call.get("prompt", ""),
                        call.get("response", ""),
                        call.get("duration_ms", ""),
                        token_usage.get("total_tokens", ""),
                        token_usage.get("prompt_tokens", ""),
                        token_usage.get("completion_tokens", ""),
                        call.get("error", ""),
                    ]
                )

                output.seek(0)
                data = output.read()
                output.seek(0)
                output.truncate(0)
                yield data

        return StreamingResponse(
            generate_csv(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=llm_calls.csv"}
        )

    def export_to_json(self, limit: int = 1000) -> StreamingResponse:
        """Export LLM calls to JSON format"""
        calls = self.db.get_calls(limit=limit)

        def generate_json():
            yield json.dumps(
                {"export_timestamp": datetime.now().isoformat(), "total_records": len(calls), "calls": calls},
                indent=2,
                default=str,
            )

        return StreamingResponse(
            generate_json(),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=llm_calls.json"},
        )

    def generate_login_html(self, error_message: str = None) -> str:
        """Generate login page HTML using Tailwind template"""
        from fastapi.templating import Jinja2Templates
        from pathlib import Path

        # Setup templates
        templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

        # Create a mock request object for template rendering
        class MockRequest:
            def __init__(self):
                self.url = type("obj", (object,), {"path": "/admin/login"})()

        request = MockRequest()

        template_response = templates.TemplateResponse(
            "login.html", {"request": request, "error": error_message, "username": ""}  # Empty username for fresh login
        )

        return template_response.body.decode("utf-8")
