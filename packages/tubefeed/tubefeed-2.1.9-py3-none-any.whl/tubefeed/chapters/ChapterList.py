import re

from .Chapter import Chapter
from ..sbapi import Segment


class ChapterList(list[Chapter]):
    def __init__(self, chapters: list[Chapter]):
        i = 0
        while i < len(chapters) - 1:
            if chapters[i].title == chapters[i + 1].title:
                chapters[i + 1].start = chapters[i].start
                del chapters[i]
            else:
                i += 1

        super().__init__(chapters)

    @staticmethod
    def from_video(title: str, duration: int) -> 'ChapterList':
        return ChapterList([
            Chapter(0, duration, title)
        ])

    @staticmethod
    def from_description(description: str, duration: int) -> 'ChapterList':
        chapters: list[tuple[int, str | None]] = []

        # hh:mm:ss chapter
        # hh:mm:ss - hh:mm:ss chapter
        chapters_iter = re.finditer(r'^\s*((\d+):)?(\d+):(\d+)( ?- ?((\d+):)?(\d+):(\d+))?\s.*?(\w.*?)$',
                                    description, re.MULTILINE)

        for chapter in chapters_iter:
            hours = int(chapter.group(2)) if chapter.group(2) is not None else 0
            minutes = int(chapter.group(3)) if chapter.group(3) is not None else 0
            seconds = int(chapter.group(4)) if chapter.group(4) is not None else 0
            title = chapter.group(10).strip()

            chapters.append(((hours * 60 + minutes) * 60 + seconds, title))

        # chapter hh:mm:ss
        # chapter hh:mm:ss - hh:mm:ss
        if len(chapters) == 0:
            chapters_iter = re.finditer(r'^\s*(\w.*?):?\s.*?((\d+):)?(\d+):(\d+)( ?- ?((\d+):)?(\d+):(\d+))?$',
                                        description, re.MULTILINE)

            for chapter in chapters_iter:
                hours = int(chapter.group(3)) if chapter.group(3) is not None else 0
                minutes = int(chapter.group(4)) if chapter.group(4) is not None else 0
                seconds = int(chapter.group(5)) if chapter.group(5) is not None else 0
                title = chapter.group(1).strip()

                chapters.append(((hours * 60 + minutes) * 60 + seconds, title))

        # padding
        chapters.append((duration, None))

        # convert to Chapter objects
        return ChapterList([
            Chapter(start, end, title)
            for (start, title), (end, _) in zip(chapters, chapters[1:])
        ])

    @staticmethod
    async def from_sponsorblock(segments: list[Segment]) -> 'ChapterList':
        return ChapterList([
            Chapter(int(segment.start), int(segment.end), segment.category.capitalize())
            for segment in segments
        ])

    def __and__(self, other: 'ChapterList') -> 'ChapterList':
        chapters = []

        sources = [self, other]
        pos = [0, 0]

        while True:
            if pos[0] < len(sources[0]) and pos[1] < len(sources[1]):
                if abs(sources[0][pos[0]].start - sources[1][pos[1]].start) < 5:
                    use = [0, 1]
                elif sources[0][pos[0]].start < sources[1][pos[1]].start:
                    use = [0]
                else:
                    use = [1]
            elif pos[0] < len(sources[0]):
                use = [0]
            elif pos[1] < len(sources[1]):
                use = [1]
            else:
                break

            start = min(sources[i][pos[i]].start for i in use)
            end = min((
                max((
                    *(
                        sources[i][pos[i]].end
                        for i in use
                        if sources[i][pos[i]].end < 5 + min((
                            *(
                                sources[i][pos[i]].end
                                for i in use
                            ),
                        ))
                    ),
                )),
                *(
                    sources[i][pos[i]].start
                    for i in (0, 1)
                    if pos[i] < len(sources[i]) and i not in use
                ),
            ))

            chapters.append(Chapter(start, end, sources[use[-1]][pos[use[-1]]].title))

            for i in use:
                sources[i][pos[i]].start = end

            for i in (0, 1):
                if pos[i] < len(sources[i]) and sources[i][pos[i]].end <= end:
                    pos[i] += 1

        return ChapterList(chapters)
