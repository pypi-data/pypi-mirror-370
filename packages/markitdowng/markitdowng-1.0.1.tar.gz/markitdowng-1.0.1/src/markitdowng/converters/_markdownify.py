import re
import io
import markdownify
import yaml
from minio import Minio
import base64
import uuid
from typing import Any, Optional
from urllib.parse import quote, unquote, urlparse, urlunparse


class _CustomMarkdownify(markdownify.MarkdownConverter):
    """
    A custom version of markdownify's MarkdownConverter. Changes include:

    - Altering the default heading style to use '#', '##', etc.
    - Removing javascript hyperlinks.
    - Truncating images with large data:uri sources.
    - Ensuring URIs are properly escaped, and do not conflict with Markdown syntax
    """

    def __init__(self, config_path: str,  **options: Any):
        # 读取配置文件
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

            minio_conf = config["minio"]
            # 初始化 MinIO 客户端
            self.minio_client = Minio(
                endpoint=minio_conf["endpoint"],
                access_key=minio_conf["access_key"],
                secret_key=minio_conf["secret_key"],
                secure=minio_conf.get("secure", True)
            )
            self.bucket_name = minio_conf["bucket_name"]
            self.endpoint = minio_conf["endpoint"]
            self.secure = minio_conf.get("secure", True)

            # 如果 bucket 不存在则创建
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
                public_policy = f"""
                            {{
                                "Version": "2012-10-17",
                                "Statement": [
                                    {{
                                        "Effect": "Allow",
                                        "Principal": "*",
                                        "Action": ["s3:GetObject"],
                                        "Resource": ["arn:aws:s3:::{self.bucket_name}/*"]
                                    }}
                                ]
                            }}
                            """
                self.minio_client.set_bucket_policy(self.bucket_name, public_policy)

        options["heading_style"] = options.get("heading_style", markdownify.ATX)
        options["keep_data_uris"] = options.get("keep_data_uris", False)
        # Explicitly cast options to the expected type if necessary
        super().__init__(**options)

    def upload_to_minio(self, image_bytes: bytes, filename: str, ext: str) -> str:
        """上传图片到MinIO并返回访问URL"""
        object_name = f"{filename}.{ext}"
        self.minio_client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            data=io.BytesIO(image_bytes),
            length=len(image_bytes),
            content_type=f"image/{ext}"
        )
        scheme = "https" if self.secure else "http"
        return f"{scheme}://{self.endpoint}/{self.bucket_name}/{object_name}"

    def convert_hn(
        self,
        n: int,
        el: Any,
        text: str,
        convert_as_inline: Optional[bool] = False,
        **kwargs,
    ) -> str:
        """Same as usual, but be sure to start with a new line"""
        if not convert_as_inline:
            if not re.search(r"^\n", text):
                return "\n" + super().convert_hn(n, el, text, convert_as_inline)  # type: ignore

        return super().convert_hn(n, el, text, convert_as_inline)  # type: ignore

    def convert_a(
        self,
        el: Any,
        text: str,
        convert_as_inline: Optional[bool] = False,
        **kwargs,
    ):
        """Same as usual converter, but removes Javascript links and escapes URIs."""
        prefix, suffix, text = markdownify.chomp(text)  # type: ignore
        if not text:
            return ""

        if el.find_parent("pre") is not None:
            return text

        href = el.get("href")
        title = el.get("title")

        # Escape URIs and skip non-http or file schemes
        if href:
            try:
                parsed_url = urlparse(href)  # type: ignore
                if parsed_url.scheme and parsed_url.scheme.lower() not in ["http", "https", "file"]:  # type: ignore
                    return "%s%s%s" % (prefix, text, suffix)
                href = urlunparse(parsed_url._replace(path=quote(unquote(parsed_url.path))))  # type: ignore
            except ValueError:  # It's not clear if this ever gets thrown
                return "%s%s%s" % (prefix, text, suffix)

        # For the replacement see #29: text nodes underscores are escaped
        if (
            self.options["autolinks"]
            and text.replace(r"\_", "_") == href
            and not title
            and not self.options["default_title"]
        ):
            # Shortcut syntax
            return "<%s>" % href
        if self.options["default_title"] and not title:
            title = href
        title_part = ' "%s"' % title.replace('"', r"\"") if title else ""
        return (
            "%s[%s](%s%s)%s" % (prefix, text, href, title_part, suffix)
            if href
            else text
        )

    def convert_img(
        self,
        el: Any,
        text: str,
        convert_as_inline: Optional[bool] = False,
        **kwargs,
    ) -> str:
        """Same as usual converter, but removes data URIs"""

        alt = el.attrs.get("alt", None) or ""
        src = el.attrs.get("src", None) or ""
        title = el.attrs.get("title", None) or ""
        title_part = ' "%s"' % title.replace('"', r"\"") if title else ""
        # if (
        #     convert_as_inline
        #     and el.parent.name not in self.options["keep_inline_images_in"]
        # ):
        #     return alt

        # Remove dataURIs
        # if src.startswith("data:") and not self.options["keep_data_uris"]:
        #     src = src.split(",")[0] + "..."

        if convert_as_inline and el.parent.name not in self.options["keep_inline_images_in"]:
            return alt

            # 如果是 Base64 图片
        if src.startswith("data:image/"):
            try:
                header, encoded = src.split(",", 1)
                ext = header.split("/")[1].split(";")[0]  # 获取文件后缀
                image_bytes = base64.b64decode(encoded)
                # 用 UUID 生成唯一文件名，避免覆盖
                # filename = alt or str(uuid.uuid4())
                filename = f"{alt}_{uuid.uuid4().hex}" if alt else str(uuid.uuid4())
                # 上传到 MinIO
                src = self.upload_to_minio(image_bytes, filename, ext)
            except Exception as e:
                print("上传Base64图片到MinIO失败:", e)

        return f"![{alt}]({src}{title_part})"
        # return "![%s](%s%s)" % (alt, src, title_part)

    def convert_soup(self, soup: Any) -> str:
        return super().convert_soup(soup)  # type: ignore
