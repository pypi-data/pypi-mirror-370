import datetime
import io
import logging
import os
import zipfile
from abc import ABC, abstractmethod
from collections.abc import Iterable

import pydantic

from mitm_tooling.definition import MITM, get_mitm_def
from mitm_tooling.representation.file import write_data_file, write_header_file
from mitm_tooling.representation.intermediate import Header, MITMData, StreamingMITMData
from mitm_tooling.utilities.io_utils import ByteSink, DataSink, FilePath, ensure_ext, use_bytes_io

logger = logging.getLogger(__name__)


class FileExport(pydantic.BaseModel, ABC):
    """
    Abstract base class for file exports of MITM data.
    """

    mitm: MITM
    filename: str

    @abstractmethod
    def write(self, sink: DataSink, **kwargs):
        pass

    def to_buffer(self) -> io.BytesIO:
        buffer = io.BytesIO()
        self.write(buffer)
        buffer.seek(0)
        return buffer

    def into_file(self, path: os.PathLike):
        self.write(path)


class ZippedExport(FileExport):
    """
    Export `MITMData` to the specific zip file format designed for MITMs.
    """

    mitm_data: MITMData

    def write(self, sink: DataSink, **kwargs):
        if not isinstance(sink, ByteSink):
            logger.error(f'Attempted to write to unsupported data sink: {sink}.')
            return

        mitm_def = get_mitm_def(self.mitm)
        with use_bytes_io(sink, expected_file_ext='.zip', mode='wb', create_file_if_necessary=True) as f:
            with zipfile.ZipFile(f, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
                with zf.open('header.csv', 'w') as hf:
                    write_header_file(self.mitm_data.header.generate_header_df(), hf)
                for c, df in self.mitm_data:
                    fn = ensure_ext(mitm_def.get_properties(c).plural, '.csv')
                    with zf.open(fn, 'w') as cf:
                        write_data_file(df, cf)
                        logger.debug(f'Wrote {len(df)} rows to {fn} (in-memory export).')


class StreamingZippedExport(FileExport):
    """
    Export `StreamingMITMData` to a streamed zip file in the format designed for MITMs.

    See also `ZippedExport`.
    """

    streaming_mitm_data: StreamingMITMData

    def write(self, sink: ByteSink, **kwargs):
        if not isinstance(sink, ByteSink):
            logger.error(f'Attempted to write to unsupported data sink: {sink}.')
            return

        mitm_def = get_mitm_def(self.mitm)
        collected_header_entries = []
        with use_bytes_io(sink, expected_file_ext='.zip', mode='wb', create_file_if_necessary=True) as f:
            with zipfile.ZipFile(f, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
                for c, concept_data in self.streaming_mitm_data:
                    fn = ensure_ext(mitm_def.get_properties(c).plural, '.csv')
                    with zf.open(fn, 'w') as cf:
                        write_data_file(concept_data.structure_df, cf, append=False)
                        for df_chunks in concept_data.chunk_iterators:
                            for df_chunk, header_entries in df_chunks:
                                collected_header_entries.extend(header_entries)
                                write_data_file(df_chunk, cf, append=True)
                                logger.debug(f'Wrote {len(df_chunk)} rows to {fn} (streaming export).')

                with zf.open('header.csv', 'w') as hf:
                    header_df = Header(
                        mitm=self.mitm, header_entries=frozenset(collected_header_entries)
                    ).generate_header_df()
                    write_header_file(header_df, hf)

    def iter_bytes(self, chunk_size: int = 65536) -> Iterable[bytes]:
        from stat import S_IFREG

        from stream_zip import ZIP_64, stream_zip

        mitm_def = get_mitm_def(self.mitm)
        collected_header_entries = []

        def files():
            modified_at = datetime.datetime.now()
            mode = S_IFREG | 0o600

            for c, concept_data in self.streaming_mitm_data:
                fn = ensure_ext(mitm_def.get_properties(c).plural, '.csv')

                def concept_file_data(concept_data=concept_data):
                    yield write_data_file(concept_data.structure_df, sink=None, append=False).encode('utf-8')
                    for df_chunks in concept_data.chunk_iterators:
                        for df_chunk, header_entries in df_chunks:
                            collected_header_entries.extend(header_entries)
                            yield write_data_file(df_chunk, sink=None, append=True).encode('utf-8')

                yield fn, modified_at, mode, ZIP_64, concept_file_data()

            header_df = Header(mitm=self.mitm, header_entries=frozenset(collected_header_entries)).generate_header_df()
            yield 'header.csv', modified_at, mode, ZIP_64, (write_header_file(header_df, sink=None).encode('utf-8'),)

        return stream_zip(files(), chunk_size=chunk_size)


def write_zip(target: FilePath, mitm_data: MITMData) -> None:
    """
    Write `mitm_data` to a zip file.

    :param target: the output file path
    :param mitm_data: the `MITMData` to write
    """
    return ZippedExport(mitm=mitm_data.header.mitm, filename=os.path.basename(target), mitm_data=mitm_data).write(
        target
    )
