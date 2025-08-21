"""
Post data parser

Parse raw post data from API responses into Post entities.
Handles complex nested structures like images and videos.
"""

import json
import logging
import re
from datetime import datetime
from typing import Any

import esprima
from lxml import etree

from ..exceptions import ParseError
from ..models.entities import Image, Post, User, Video
from .user import UserParser


class PostParser:
    """Parse raw post data into Post entities

    Responsibilities:
    - Extract post data from API response
    - Parse nested user data
    - Handle image/video attachments
    - Convert timestamps
    - Clean HTML from text
    """

    def __init__(self, logger: logging.Logger | None = None):
        self._logger = logger or logging.getLogger(__name__)
        self._user_parser = UserParser(logger)

    def parse(self, raw_data: dict[str, Any]) -> Post:
        """Parse raw post data into Post entity

        Args:
            raw_data: Raw post data from API

        Returns:
            Post entity

        Raises:
            ParseError: When required fields are missing or invalid
        """
        try:
            # Extract required fields
            post_id = self._extract_id(raw_data)
            created_at = self._extract_created_at(raw_data)
            text = self._extract_text(raw_data)
            user = self._extract_user(raw_data)

            # Extract optional fields
            text_raw = raw_data.get("text_raw")
            region_name = raw_data.get("region_name")
            source = self._clean_source(raw_data.get("source"))

            # Extract counts
            reposts_count = int(raw_data.get("reposts_count", 0))
            comments_count = int(raw_data.get("comments_count", 0))
            attitudes_count = int(raw_data.get("attitudes_count", 0))

            # Extract media
            images = self._extract_images(raw_data)
            video = self._extract_video(raw_data)

            return Post(
                id=post_id,
                created_at=created_at,
                text=text,
                text_raw=text_raw,
                region_name=region_name,
                source=source,
                reposts_count=reposts_count,
                comments_count=comments_count,
                attitudes_count=attitudes_count,
                user=user,
                images=images,
                video=video,
            )

        except (KeyError, ValueError, TypeError) as e:
            self._logger.error(f"Failed to parse post data: {e}")
            raise ParseError(f"Invalid post data: {e}")

    def parse_detail_page(self, html_content: str) -> Post:
        """Parse post from detail page HTML

        Args:
            html_content: HTML content from detail page

        Returns:
            Post entity

        Raises:
            ParseError: When data extraction fails
        """
        try:
            # Extract render_data using esprima for safe parsing
            render_data = self._extract_render_data_safe(html_content)
            status_data = render_data.get("status")

            if not status_data:
                raise ParseError("No status data in render data")

            return self.parse(status_data)

        except Exception as e:
            self._logger.error(f"Failed to parse detail page: {e}")
            raise ParseError(f"Failed to parse detail page: {e}")

    def _extract_render_data_safe(self, html_content: str) -> dict:
        """Safely extract $render_data using lxml parser

        Args:
            html_content: HTML content containing JavaScript

        Returns:
            Parsed render_data object

        Raises:
            ParseError: When extraction fails
        """
        try:
            # Parse HTML with lxml
            parser = etree.HTMLParser()
            tree = etree.fromstring(html_content, parser)

            # Find all script tags
            script_elements = tree.xpath("//script")
            self._logger.debug(f"Found {len(script_elements)} script tags")

            for i, script_elem in enumerate(script_elements):
                script_content = script_elem.text
                if not script_content or "$render_data" not in script_content:
                    continue

                self._logger.debug(f"Processing script {i+1} with $render_data")

                try:
                    # Use esprima to safely parse JavaScript
                    tree = esprima.parseScript(
                        script_content,
                        options={
                            "tolerant": True,  # Continue parsing on errors
                            "range": True,  # Include source position info
                        },
                    )

                    self._logger.debug(
                        f"Successfully parsed script {i+1} into AST with {len(tree.body)} nodes"
                    )

                    # Find $render_data variable declaration
                    for node_idx, node in enumerate(tree.body):
                        if self._is_render_data_declaration(node):
                            self._logger.debug(
                                f"Found $render_data declaration in node {node_idx}"
                            )
                            json_str = self._extract_json_from_ast(node, script_content)
                            if json_str:
                                self._logger.debug(
                                    f"Extracted JSON string: {len(json_str)} characters"
                                )
                                try:
                                    # The extracted JSON is already the first array element (object)
                                    render_data_obj = json.loads(json_str)
                                    if isinstance(render_data_obj, dict):
                                        self._logger.debug(
                                            "Successfully parsed render_data object"
                                        )
                                        return render_data_obj
                                    else:
                                        self._logger.warning(
                                            f"render_data is not a dict: {type(render_data_obj)}"
                                        )
                                except json.JSONDecodeError as je:
                                    self._logger.error(f"JSON parsing failed: {je}")
                                    raise ParseError(
                                        f"Invalid JSON in render_data: {je}"
                                    )
                            else:
                                self._logger.debug(
                                    "Failed to extract JSON from AST node"
                                )

                except esprima.Error as e:
                    self._logger.debug(f"Esprima parsing failed for script {i+1}: {e}")
                    continue
                except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
                    self._logger.debug(f"Data extraction failed for script {i+1}: {e}")
                    continue

            raise ParseError("Could not find or parse $render_data in any script tag")

        except etree.XMLSyntaxError as e:
            self._logger.error(f"HTML parsing failed: {e}")
            raise ParseError(f"Invalid HTML content: {e}")

    def _is_render_data_declaration(self, node) -> bool:
        """Check if AST node is $render_data variable declaration"""
        if (
            node.type != "VariableDeclaration"
            or len(node.declarations) == 0
            or not hasattr(node.declarations[0].id, "name")
            or node.declarations[0].id.name != "$render_data"
            or not node.declarations[0].init
        ):
            return False

        init = node.declarations[0].init

        # Handle: var $render_data = [...][0] || {}
        if init.type == "LogicalExpression" and init.operator == "||":
            # Check left side: [...][0]
            left = init.left
            if (
                left.type == "MemberExpression"
                and left.object.type == "ArrayExpression"
            ):
                return True

        # Handle: var $render_data = [...][0]
        elif init.type == "MemberExpression" and init.object.type == "ArrayExpression":
            return True

        return False

    def _extract_json_from_ast(self, node, script_content: str) -> str:
        """Extract JSON string from AST node"""
        try:
            init = node.declarations[0].init
            array_expr = None

            # Handle: var $render_data = [...][0] || {}
            if init.type == "LogicalExpression" and init.operator == "||":
                # Get array from left side
                left = init.left
                if (
                    left.type == "MemberExpression"
                    and left.object.type == "ArrayExpression"
                ):
                    array_expr = left.object

            # Handle: var $render_data = [...][0]
            elif (
                init.type == "MemberExpression"
                and init.object.type == "ArrayExpression"
            ):
                array_expr = init.object

            if array_expr and array_expr.elements and len(array_expr.elements) > 0:
                # Extract the first array element's source code
                first_element = array_expr.elements[0]
                start = first_element.range[0]
                end = first_element.range[1]
                return script_content[start:end]

        except (AttributeError, IndexError, KeyError) as e:
            self._logger.debug(f"Failed to extract JSON from AST: {e}")

        return None

    def _extract_id(self, data: dict[str, Any]) -> int:
        """Extract and validate post ID"""
        post_id = data.get("id")
        if not post_id:
            raise ValueError("Missing post ID")
        return int(post_id)

    def _extract_created_at(self, data: dict[str, Any]) -> datetime:
        """Extract and parse created_at timestamp"""
        created_at = data.get("created_at")
        if not created_at:
            raise ValueError("Missing created_at")

        # Try different datetime formats
        formats = [
            "%a %b %d %H:%M:%S %z %Y",  # Mon Jan 01 12:00:00 +0800 2024
            "%Y-%m-%d %H:%M:%S%z",  # 2025-06-29 06:46:38+08:00
        ]

        for fmt in formats:
            try:
                return datetime.strptime(created_at, fmt)
            except ValueError:
                continue

        raise ValueError(f"Cannot parse timestamp: {created_at}")

    def _extract_text(self, data: dict[str, Any]) -> str:
        """Extract and clean post text"""
        text = data.get("text", "")
        return str(text).strip()

    def _extract_user(self, data: dict[str, Any]) -> User:
        """Extract user data"""
        user_data = data.get("user")
        if not user_data:
            raise ValueError("Missing user data")

        return self._user_parser.parse(user_data)

    def _clean_source(self, source: str | None) -> str | None:
        """Clean HTML tags from source field"""
        if not source:
            return None

        # Remove HTML tags
        match = re.search(r">(.*?)</a>", source)
        if match:
            return match.group(1)

        return source

    def _extract_images(self, data: dict[str, Any]) -> list[Image]:
        """Extract image attachments"""
        images = []

        pic_num = int(data.get("pic_num", 0))
        if pic_num == 0:
            return images

        pic_ids = data.get("pic_ids", [])
        pic_infos = data.get("pic_infos", {})

        for pic_id in pic_ids:
            if pic_id in pic_infos:
                try:
                    image = self._parse_image(pic_id, pic_infos[pic_id])
                    images.append(image)
                except (KeyError, ValueError, TypeError) as e:
                    self._logger.warning(f"Failed to parse image {pic_id}: {e}")
                except ParseError as e:
                    self._logger.warning(f"Invalid image data for {pic_id}: {e}")

        return images

    def _parse_image(self, pic_id: str, pic_info: dict[str, Any]) -> Image:
        """Parse individual image info"""
        # Extract different sizes
        thumbnail = pic_info.get("thumbnail", {})
        large = pic_info.get("large", {})
        original = pic_info.get("original", {})

        return Image(
            id=pic_id,
            thumbnail_url=thumbnail.get("url", ""),
            large_url=large.get("url", ""),
            original_url=original.get("url", ""),
            width=int(large.get("width", 0)),
            height=int(large.get("height", 0)),
        )

    def _extract_video(self, data: dict[str, Any]) -> Video | None:
        """Extract video attachment"""
        page_info = data.get("page_info")
        if not page_info:
            return None

        try:
            duration = float(page_info.get("duration", 0))
            play_count = page_info.get("play_count", 0)

            # Extract video URLs from media_info
            urls = {}
            media_info = page_info.get("media_info", {})
            for quality, info in media_info.items():
                if isinstance(info, dict) and "url" in info:
                    urls[quality] = info["url"]

            if not urls:
                return None

            return Video(duration=duration, play_count=play_count, urls=urls)

        except (KeyError, ValueError, TypeError) as e:
            self._logger.warning(f"Failed to parse video info: {e}")
            return None
        except ParseError as e:
            self._logger.warning(f"Invalid video data: {e}")
            return None
