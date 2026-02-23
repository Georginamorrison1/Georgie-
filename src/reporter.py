import anthropic


class HRReporter:
    """Uses Claude to generate HR reports and answer workforce questions."""

    MODEL = "claude-opus-4-6"

    def __init__(self):
        self._client = anthropic.Anthropic()

    # ------------------------------------------------------------------
    # Public report methods
    # ------------------------------------------------------------------

    def generate_headcount_report(self, summary: dict) -> None:
        """Stream a headcount report from aggregated employee data."""
        prompt = f"""You are an HR analytics expert. Generate a clear, structured headcount report from the data below.

Employee Data:
- Total headcount: {summary["total"]}
- By department: {summary["by_department"]}
- By site/location: {summary["by_site"]}
- By employment type: {summary["by_employment_type"]}
- New hires in last 90 days ({len(summary["recent_hires_last_90_days"])} total):
{self._format_list(summary["recent_hires_last_90_days"], limit=20)}

Write the report in plain text with clear sections:
1. Executive Summary
2. Department Breakdown
3. Geographic Distribution
4. Recent Growth (new hires)
5. Key Observations"""
        self._stream(prompt)

    def generate_timeoff_report(self, summary: dict) -> None:
        """Stream a time-off summary report."""
        prompt = f"""You are an HR analytics expert. Generate a clear time-off summary report from the data below.

Time-Off Data:
- Employees out today: {summary["out_today_count"]}
- Names of employees out today: {summary["out_today"] or "None"}
- Total time-off requests (last 30 days): {summary["requests_total"]}
- Requests by type: {summary["by_type"]}

Write the report in plain text with clear sections:
1. Today's Absence Summary
2. Time-Off Trends (last 30 days)
3. Key Observations
4. Workforce Planning Notes"""
        self._stream(prompt)

    def answer_query(self, question: str, summary: dict) -> None:
        """Stream an answer to an arbitrary HR question using workforce data."""
        prompt = f"""You are an HR analytics assistant with access to the company's workforce data.

Workforce Summary:
- Total employees: {summary["total"]}
- Departments: {summary["by_department"]}
- Sites: {summary["by_site"]}
- Employment types: {summary["by_employment_type"]}
- Recent hires (last 90 days): {len(summary["recent_hires_last_90_days"])}

Question: {question}

Answer concisely and accurately, drawing on the data above. If the data does not contain enough detail to fully answer the question, say so clearly."""
        self._stream(prompt)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _stream(self, prompt: str) -> None:
        with self._client.messages.stream(
            model=self.MODEL,
            max_tokens=4096,
            thinking={"type": "adaptive"},
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
        print()

    @staticmethod
    def _format_list(items: list[dict], limit: int = 20) -> str:
        if not items:
            return "  (none)"
        lines = []
        for item in items[:limit]:
            parts = [f"{k}: {v}" for k, v in item.items() if v]
            lines.append("  - " + ", ".join(parts))
        if len(items) > limit:
            lines.append(f"  ... and {len(items) - limit} more")
        return "\n".join(lines)
