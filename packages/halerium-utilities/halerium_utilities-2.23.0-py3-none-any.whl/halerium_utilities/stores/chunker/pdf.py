import io
import uuid
from typing import Iterable, List, Literal, Optional, Tuple

import pymupdf
from pydantic.v1 import BaseModel, Field

from PIL import Image
import base64

from halerium_utilities.prompt.models import call_model
from halerium_utilities.stores.chunker import Chunker, Document
from halerium_utilities.stores.chunker.exceptions import ChunkingException


class PDFArguments(BaseModel):
    filename: str = Field(default=None, required=True, description="Path of the file in Halerium", title="Filename")
    chunk_size: int = Field(default=10000, description="The chunking size", title="Chunk Size")
    chunk_overlap: int = Field(default=5000, description="The overlap of the chunks", title="Chunk Overlap")

    table_extractors: List[Literal["pymupdf"]] = Field(default=[], description="A list of table extractors to use")
    text_extractors: List[Literal["google", "pymupdf"]] = Field(default=["pymupdf"], description="List of text extractors to use")
    add_images: bool = Field(default=False, description="If images shall be added to the information store", title="Add Images")
    image_dpi: int = Field(default=300, description="The image resolution dpi.", title="Image extractor resolution")


def get_image(page, dpi=100, bbox: Optional[Tuple[int, int, int, int]] = None):
    scale_factor = dpi / 72
    matrix = pymupdf.Matrix(scale_factor, scale_factor)
    img = page.get_pixmap(matrix=matrix)
    img = Image.frombytes("RGB", [img.width, img.height], img.samples)

    if bbox is not None:
        img = img.crop(tuple(int(x * scale_factor) for x in bbox))

    fp = io.BytesIO()
    img.save(fp, "JPEG")
    fp.seek(0)

    b64_img = base64.b64encode(fp.read())
    fp.close()
    return b64_img.decode("latin1")


def ocr_b64(b64_img):
    gen = call_model("google-vision", body={"image": b64_img}, parse_data=True)

    response = None
    for event in gen:
        if event.event == 'data':
            response = event.data
            #break
        if event.event == 'conclusion':
            conclusion_payload = event.data
            if 'error' in conclusion_payload:
                raise ChunkingException('ERROR: ' + conclusion_payload['error'])

    return response


def ocr(filename):
    with open(filename, "rb") as f:
        image = base64.b64encode(f.read()).decode()

    return ocr_b64(image)


class PDFChunker(Chunker):

    def __init__(self, params: PDFArguments):
        self.params = params

    def chunk(self) -> Iterable[Document]:
        doc = pymupdf.open(self.params.filename)

        for page in doc:
            page_metadata = dict(
                filename=self.params.filename,
                page=str(page.number),
            )
            if self.params.add_images:
                page_metadata["image_b64"] = get_image(page, dpi=self.params.image_dpi)

            if "google" in self.params.text_extractors:
                content = ocr_b64(get_image(page, dpi=self.params.image_dpi))
                content = content["responses"][0]["fullTextAnnotation"]["text"]
                yield Document(content=content, metadata=page_metadata)

            if "pymupdf" in self.params.text_extractors:
                yield Document(content=page.get_text(), metadata=page_metadata)

            if "pymupdf" in self.params.table_extractors:
                for tab in page.find_tables():
                    table_uuid = uuid.uuid4().hex
                    df = tab.to_pandas()
                    content = df.to_markdown()

                    metadata = dict(
                        **page_metadata,
                        table_id=table_uuid,
                    )

                    if self.params.add_images:
                        metadata["image_b64"] = get_image(page, dpi=self.params.image_dpi, bbox=tab.bbox)

                    yield Document(content=content, metadata=metadata)

