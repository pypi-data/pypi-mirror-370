from aiohttp import ClientSession, ContentTypeError

from .Segment import Segment


class SponsorBlock:
    BASE_URL: str = 'https://sponsor.ajay.app/api/'

    async def __aenter__(self):
        self._session: ClientSession = ClientSession(SponsorBlock.BASE_URL)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.close()

    async def skip_segments(self, id: str) -> list[Segment]:
        try:
            async with self._session.get('skipSegments', params={'videoID': id}) as request:
                response = await request.json()

            return [Segment(segment) for segment in response]

        except ContentTypeError as e:
            if e.status == 404:
                return []
            else:
                raise e
