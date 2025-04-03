import re
import html
import markdown
from bs4 import BeautifulSoup


class MarkdownConverter:
    """Class that provides markdown conversion functionality with improved code block detection"""

    def __init__(self):
        self.md = markdown.Markdown(extensions=["tables", "fenced_code"])

    def to_markdown(self, text):
        """
        Convert plain text to markdown with enhanced code block detection

        Args:
            text (str): Plain text to convert

        Returns:
            str: Markdown formatted text
        """
        # Clean the text
        text = text.strip()

        # Process paragraphs - each line break becomes a new paragraph
        paragraphs = re.split(r"\n\s*\n", text)
        result = []

        # Process each paragraph
        for para in paragraphs:
            lines = para.strip().split("\n")

            # Check if this is a code block using improved detection
            if self._is_code_block(para, lines):
                code_lang = self._detect_language(para, lines)
                formatted_para = f"```{code_lang}\n{para}\n```"
                result.append(formatted_para)

            # Check for bulleted lists (lines starting with - or *)
            elif all(re.match(r"^\s*[-*]\s", line) for line in lines if line.strip()):
                # It's a bulleted list, keep as is
                result.append(para)

            # Check for numbered lists (lines starting with numbers)
            elif all(
                re.match(r"^\s*\d+[.)]\s", line) for line in lines if line.strip()
            ):
                # It's a numbered list, keep as is
                result.append(para)

            # Not a list or code block, format as paragraph
            else:
                # Process headings - look for lines that could be headings
                processed_lines = []
                for line in lines:
                    line = line.strip()

                    # Empty line
                    if not line:
                        processed_lines.append("")
                        continue

                    # Check if it looks like a heading (short line, no ending punctuation)
                    if (
                        len(line) < 60
                        and not re.search(r"[.,:;]$", line)
                        and not re.search(
                            r"\b(and|or|but|that|with|from|by|as|on)\b$", line.lower()
                        )
                    ):
                        # Looks like a heading - determine level based on importance
                        if len(processed_lines) == 0:  # First line is a title
                            processed_lines.append(f"# {line}")
                        else:
                            processed_lines.append(f"## {line}")
                    else:
                        processed_lines.append(line)

                result.append("\n".join(processed_lines))

        # Join paragraphs with double newlines
        markdown_text = "\n\n".join(result)

        # Enhance the formatting with additional markdown features
        markdown_text = self._enhance_formatting(markdown_text)

        return markdown_text

    def _is_code_block(self, text, lines):
        """
        Enhanced code block detection with machine learning-inspired rules

        Args:
            text (str): Text to check
            lines (list): Lines of the text

        Returns:
            bool: True if the text is a code block
        """
        # Code pattern indicators with point scoring system
        score = 0

        # Check for common programming language constructs
        if re.search(
            r"\b(def|class|function|if|for|while|try|except|import|from)\b", text
        ):
            score += 5

        # Check for variable assignments
        if re.search(r"[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*", text):
            score += 3

        # Check for programming language punctuation patterns
        if re.search(r"[{}\[\]();]", text):
            score += 2

        # Check for indentation patterns (spaces at the beginning of lines)
        if any(re.match(r"^\s{2,}", line) for line in lines):
            score += 3

        # Check for programming keywords
        programming_keywords = [
            "return",
            "print",
            "var",
            "let",
            "const",
            "async",
            "await",
            "public",
            "private",
            "static",
            "void",
            "int",
            "float",
            "string",
            "bool",
            "True",
            "False",
            "None",
            "null",
            "undefined",
            "this",
            "self",
            "lambda",
            "map",
            "filter",
            "reduce",
        ]
        for keyword in programming_keywords:
            if re.search(r"\b" + re.escape(keyword) + r"\b", text):
                score += 1

        # Check for code comments
        if re.search(r"^\s*(#|//|/\*|\*)", text, re.MULTILINE):
            score += 3

        # Check for method calls
        if re.search(r"[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*\s*\(", text):
            score += 4

        # Check for common design patterns in code
        # Example: queue = deque() followed by queue.append()
        if (
            len(lines) >= 2
            and any("=" in line for line in lines)
            and any("." in line for line in lines)
        ):
            score += 2

        # Make final determination based on score
        return score >= 5

    def _detect_language(self, text, lines):
        """
        Detect the programming language of the code block

        Args:
            text (str): Code text
            lines (list): Lines of the code

        Returns:
            str: Language identifier for markdown
        """
        # Python indicators
        if re.search(
            r"\b(def|class|import|from|if __name__|print)\b", text
        ) or re.search(r":\s*$", text, re.MULTILINE):
            return "py"

        # JavaScript/TypeScript indicators
        if re.search(
            r"\b(function|const|let|var|export|import from|=>)\b", text
        ) or re.search(r";\s*$", text, re.MULTILINE):
            if re.search(r"\b(interface|type|<T>|:string|:number|:boolean)\b", text):
                return "ts"
            return "js"

        # HTML indicators
        if re.search(r"<[a-zA-Z]+[^>]*>.*?</[a-zA-Z]+>", text, re.DOTALL) or re.search(
            r"<[a-zA-Z]+[^>]*/>", text
        ):
            return "html"

        # CSS indicators
        if re.search(r"[a-zA-Z-]+\s*{\s*[a-zA-Z-]+\s*:\s*[^;]+;\s*}", text, re.DOTALL):
            return "css"

        # Java/C# indicators
        if re.search(r"\b(public|private|class|static|void)\b", text) and re.search(
            r"{\s*$", text, re.MULTILINE
        ):
            if re.search(r"\b(System\.out\.println|String\[\]|args)\b", text):
                return "java"
            if re.search(r"\b(Console|WriteLine|namespace|using System)\b", text):
                return "csharp"

        # C/C++ indicators
        if re.search(r"\b(include|printf|scanf|malloc|int main|void main)\b", text):
            if re.search(r"\b(std::|cout|cin|vector|string)\b", text):
                return "cpp"
            return "c"

        # SQL indicators
        if re.search(
            r"\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|JOIN)\b", text, re.IGNORECASE
        ):
            return "sql"

        # Shell/Bash indicators
        if (
            text.startswith("$")
            or text.startswith("#!")
            or re.search(r"\b(chmod|chown|sudo|apt|yum|brew)\b", text)
        ):
            return "bash"

        # Default to empty string if language can't be detected
        return ""

    def _enhance_formatting(self, markdown_text):
        """
        Apply additional formatting enhancements to the markdown text

        Args:
            markdown_text (str): Markdown text to enhance

        Returns:
            str: Enhanced markdown text
        """
        # Emphasize important phrases (text between * or _)
        markdown_text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"**\1**", markdown_text)
        markdown_text = re.sub(r"(?<!_)_([^_\n]+)_(?!_)", r"*\1*", markdown_text)

        # Add code formatting for technical terms
        markdown_text = re.sub(r"`([^`\n]+)`", r"`\1`", markdown_text)

        # Format URLs
        markdown_text = re.sub(r"(https?://[^\s]+)", r"[\1](\1)", markdown_text)

        # Fix any HTML tags to use single backticks
        markdown_text = re.sub(r"<(\w+)[^>]*>", r"`<\1>`", markdown_text)
        markdown_text = re.sub(r"</(\w+)>", r"`</\1>`", markdown_text)

        return markdown_text

    def to_text(self, markdown_text):
        """
        Convert markdown to plain text

        Args:
            markdown_text (str): Markdown text to convert

        Returns:
            str: Plain text
        """
        # Convert markdown to HTML
        html_content = self.md.convert(markdown_text)

        # Use BeautifulSoup to extract text from HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # Process different HTML elements
        for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            # Format headings with newlines
            tag.insert_before("\n\n")
            tag.insert_after("\n")

        for tag in soup.find_all(["p", "div"]):
            # Format paragraphs with newlines
            tag.insert_before("\n")
            tag.insert_after("\n")

        for tag in soup.find_all("li"):
            # Format list items
            if tag.parent.name == "ol":
                # Numbered list
                index = 1
                for i, li in enumerate(tag.parent.find_all("li")):
                    if li == tag:
                        index = i + 1
                        break
                tag.insert_before(f"{index}. ")
            else:
                # Bulleted list
                tag.insert_before("- ")
            tag.insert_after("\n")

        for tag in soup.find_all("pre"):
            # Format code blocks
            tag.insert_before("\n")
            tag.insert_after("\n")

        for tag in soup.find_all("code"):
            # Inline code - preserve backticks
            if tag.parent.name == "pre":
                # This is a code block, preserve formatting
                pass
            else:
                # Inline code
                tag.insert_before("`")
                tag.insert_after("`")

        for tag in soup.find_all("a"):
            # Links - show URL in parentheses after the text
            if tag.string and tag.get("href"):
                tag.string.replace_with(f"{tag.string} ({tag.get('href')})")

        # Extract text and clean up whitespace
        text = soup.get_text()

        # Remove excessive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Unescape HTML entities
        text = html.unescape(text)

        return text.strip()

    def convert(self, text, mode="to_markdown"):
        """
        Convert text based on the specified mode

        Args:
            text (str): Text to convert
            mode (str): 'to_markdown' or 'to_text'

        Returns:
            str: Converted text
        """
        if mode == "to_markdown":
            return self.to_markdown(text)
        elif mode == "to_text":
            return self.to_text(text)
        else:
            raise ValueError(f"Unsupported conversion mode: {mode}")
