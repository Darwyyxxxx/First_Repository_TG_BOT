import logging
import os

logger = logging.getLogger(__name__)


def _get_part_text(text: str, start: int, page_size: int) -> tuple[str, int]:
    end_sings = ".,!:;?"
    max_end = min(len(text), start + page_size)
    chunk = text[start:max_end]

    last_good = -1
    i=0
    while i < len(chunk):
        if chunk[i] in end_sings:
            while i+1 < len(chunk) and chunk[i+1] in end_sings:
                i+=1
            seq_end = i

            after_seq = start + seq_end + 1
            if(
                after_seq == len(text)
                or text[after_seq].isspace()
                or text[after_seq].isalpha()
            ):
                last_good = seq_end
        i+=1

    if last_good != -1:
        page_text = chunk[: last_good + 1]
    else:
        page_text = chunk
    return page_text, len(page_text)

def prepare_book(path: str,page_size:int = 1050) -> dict[int,str]:
    try:
        with open(file=os.path.normpath(path), mode="r", encoding="utf-8") as file:
            text = file.read()
    except Exception as e:
        logger.error("Error reading a book: %s", e)
        raise e

    book ={}
    start, page_number =0,1

    while start < len(text):
        page_text, actual_page_size =_get_part_text(text, start,page_size)
        start += actual_page_size
        book[page_number] = page_text.strip()
        page_number +=1

    return book