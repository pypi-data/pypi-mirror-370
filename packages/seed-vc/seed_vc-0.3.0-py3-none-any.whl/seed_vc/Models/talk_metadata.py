from typing import Optional


class TalkMetadata:
    def __init__(self, talk_id: str, sentence_index: Optional[int], last_item: bool):
        self.talk_id = talk_id
        self.last_item = last_item
        self.sentence_index = sentence_index

    def convert_to_not_last(self):
        return TalkMetadata(self.talk_id, self.sentence_index, False)
