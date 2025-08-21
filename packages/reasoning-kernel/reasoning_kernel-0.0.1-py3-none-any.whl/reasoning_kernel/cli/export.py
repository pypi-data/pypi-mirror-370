"""
Export functionality for MSA Reasoning Engine CLI
Provides export capabilities for results in various formats
"""
import json
import os
from typing import Dict, Any, List
from datetime import datetime

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

from reasoning_kernel.cli.ui import UIManager


def export_to_json(data: Dict[str, Any], output_path: str, ui_manager: UIManager) -> bool:
    """Export data to JSON format"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        
        ui_manager.print_success(f"Results exported to JSON: {output_path}")
        return True
    except Exception as e:
        ui_manager.print_error(f"Failed to export to JSON: {e}")
        return False


def export_to_markdown(data: Dict[str, Any], output_path: str, ui_manager: UIManager) -> bool:
    """Export data to Markdown format"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        markdown_content = _format_data_as_markdown(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        ui_manager.print_success(f"Results exported to Markdown: {output_path}")
        return True
    except Exception as e:
        ui_manager.print_error(f"Failed to export to Markdown: {e}")
        return False


def export_to_pdf(data: Dict[str, Any], output_path: str, ui_manager: UIManager) -> bool:
    """Export data to PDF format"""
    if not WEASYPRINT_AVAILABLE:
        ui_manager.print_warning("WeasyPrint not available. PDF export requires weasyprint package.")
        ui_manager.print_info("Install with: pip install weasyprint")
        return False
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # First create HTML content
        html_content = _format_data_as_html(data)
        
        # Convert HTML to PDF
        HTML(string=html_content).write_pdf(output_path)
        
        ui_manager.print_success(f"Results exported to PDF: {output_path}")
        return True
    except Exception as e:
        ui_manager.print_error(f"Failed to export to PDF: {e}")
        return False


def _format_data_as_markdown(data: Dict[str, Any]) -> str:
    """Format data as Markdown"""
    lines = []
    
    # Header
    lines.append("# MSA Reasoning Engine Results")
    lines.append(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Session information
    if "session_id" in data:
        lines.append(f"## Session: {data['session_id']}")
        lines.append("")
    
    # Mode information
    if "mode" in data:
        lines.append(f"**Mode:** {data['mode']}")
        lines.append("")
    
    # Knowledge extraction results
    if "knowledge_extraction" in data:
        knowledge = data["knowledge_extraction"]
        lines.append("## Knowledge Extraction")
        lines.append("")
        
        # Entities
        if "entities" in knowledge and knowledge["entities"]:
            lines.append("### Entities")
            lines.append("")
            lines.append("| Entity | Type | Description |")
            lines.append("|--------|------|-------------|")
            for entity_name, entity_info in knowledge["entities"].items():
                entity_type = entity_info.get("type", "Unknown")
                description = entity_info.get("description", "No description")
                lines.append(f"| {entity_name} | {entity_type} | {description} |")
            lines.append("")
        
        # Relationships
        if "relationships" in knowledge and knowledge["relationships"]:
            lines.append("### Relationships")
            lines.append("")
            lines.append("| Source | Relationship | Target |")
            lines.append("|--------|--------------|--------|")
            for rel in knowledge["relationships"]:
                source = rel.get("source", "Unknown")
                relationship = rel.get("relationship", "Unknown")
                target = rel.get("target", "Unknown")
                lines.append(f"| {source} | {relationship} | {target} |")
            lines.append("")
    
    # Confidence analysis
    if "confidence_analysis" in data:
        confidence = data["confidence_analysis"]
        lines.append("## Confidence Analysis")
        lines.append("")
        lines.append(f"Overall Confidence: {confidence.get('overall_confidence', 0.0):.3f}")
        lines.append("")
        
        if "component_confidence" in confidence:
            lines.append("### Component Confidence")
            lines.append("")
            lines.append("| Component | Confidence |")
            lines.append("|-----------|------------|")
            for component, score in confidence["component_confidence"].items():
                lines.append(f"| {component} | {score:.3f} |")
            lines.append("")
    
    # Raw data section
    lines.append("## Raw Data")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(data, indent=2, default=str))
    lines.append("```")
    
    return "\n".join(lines)


def _format_data_as_html(data: Dict[str, Any]) -> str:
    """Format data as HTML"""
    # Convert markdown to HTML for simplicity
    markdown_content = _format_data_as_markdown(data)
    
    # Simple conversion from markdown to HTML
    html_lines = []
    html_lines.append("<!DOCTYPE html>")
    html_lines.append("<html>")
    html_lines.append("<head>")
    html_lines.append("<meta charset='UTF-8'>")
    html_lines.append("<title>MSA Reasoning Engine Results</title>")
    html_lines.append("<style>")
    html_lines.append("body { font-family: Arial, sans-serif; margin: 40px; }")
    html_lines.append("h1, h2, h3 { color: #2c3e50; }")
    html_lines.append("table { border-collapse: collapse; width: 100%; margin: 20px 0; }")
    html_lines.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
    html_lines.append("th { background-color: #f2f2f2; }")
    html_lines.append("pre { background-color: #f5f5f5; padding: 10px; overflow-x: auto; }")
    html_lines.append("</style>")
    html_lines.append("</head>")
    html_lines.append("<body>")
    
    # Convert markdown-like syntax to HTML
    in_code_block = False
    for line in markdown_content.split("\n"):
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("**") and line.endswith("**"):
            content = line[2:-2]
            if ":" in content:
                parts = content.split(":", 1)
                html_lines.append(f"<p><strong>{parts[0]}:</strong> {parts[1].strip()}</p>")
            else:
                html_lines.append(f"<p><strong>{content}</strong></p>")
        elif line.startswith("|") and "|" in line:
            if "<table>" not in html_lines[-1]:
                html_lines.append("<table>")
            html_lines.append("<tr>")
            cells = [cell.strip() for cell in line.split("|") if cell.strip()]
            for cell in cells:
                if "----" in cell:
                    continue
                html_lines.append(f"<td>{cell}</td>")
            html_lines.append("</tr>")
        elif line == "":
            if "<table>" in html_lines[-2]:
                html_lines.append("</table>")
            else:
                html_lines.append("<br>")
        elif line.startswith("```"):
            if not in_code_block:
                html_lines.append("<pre><code>")
                in_code_block = True
            else:
                html_lines.append("</code></pre>")
                in_code_block = False
        else:
            if in_code_block:
                html_lines.append(line)
            else:
                html_lines.append(f"<p>{line}</p>")
    
    html_lines.append("</body>")
    html_lines.append("</html>")
    
    return "\n".join(html_lines)


def export_session_history(session_data: List[Dict[str, Any]], output_path: str, format_type: str, ui_manager: UIManager) -> bool:
    """Export session history to specified format"""
    try:
        if format_type == "json":
            return export_to_json(session_data, output_path, ui_manager)
        elif format_type == "md":
            return export_to_markdown({"sessions": session_data}, output_path, ui_manager)
        elif format_type == "pdf":
            return export_to_pdf({"sessions": session_data}, output_path, ui_manager)
        else:
            ui_manager.print_error(f"Unsupported export format: {format_type}")
            return False
    except Exception as e:
        ui_manager.print_error(f"Failed to export session history: {e}")
        return False