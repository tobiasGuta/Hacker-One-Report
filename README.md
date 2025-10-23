# Hacker-One-Report
A small Flask web app for writing vulnerability reports with a live Markdown editor and preview. It ships with two built-in presentation styles a spooky Halloween theme and a clean HackerOne-style report and lets you add your own custom style(s).

# Features

- Two built-in themes:
- Halloween: themed UI, spooky fonts/colors, and a styled rendered preview.
- HackerOne-style: clean, report-focused formatting suitable for disclosure platforms.
- Live Markdown preview (GitHub Flavored Markdown via marked.js) with support for tables, code blocks, and custom ==highlight== markup.
- Slash-triggered floating snippet menu to quickly insert predefined Markdown snippets (headers, lists, code, tables, attachments, mentions, CVE/CWE).
- Generate a final markdown report page with raw editable markdown, rendered preview, copy and download options.
- Easy to extend: add or modify CSS and template markup to create additional themes or tweak existing ones.
