import traceback
from typing import Union, List, Optional

from seppl import init_initializable, Initializable, Session
from ._reader import Reader
from ._filter import Filter, MultiFilter
from ._writer import Writer, StreamWriter, BatchWriter


def _stream_execution(reader: Reader, filter_: Optional[Filter], writer: Optional[Writer], session: Session):
    """
    Executes the pipeline in streaming mode.

    :param reader: the reader to use
    :type reader: Reader
    :param filter_: the filter to use
    :type filter_: list or Filter
    :param writer: the writer to use
    :type writer: Writer
    :param session: the session object to use
    :type session: Session
    """
    if writer is not None:
        if not isinstance(writer, StreamWriter):
            raise Exception("Not a stream writer: %s" % str(type(writer)))

    while not reader.has_finished():
        for item in reader.read():
            if item is None:
                continue
            session.count += 1
            if (filter_ is not None) and (item is not None):
                item = filter_.process(item)
            if item is not None:
                if writer is not None:
                    writer.write_stream(item)
            if session.count % session.options.update_interval == 0:
                session.logger.info("%d records processed..." % session.count)


def _batch_execution(reader: Reader, filter_: Optional[Filter], writer: Optional[Writer], session: Session):
    """
    Executes the pipeline in batch mode.

    :param reader: the reader to use
    :type reader: Reader
    :param filter_: the filter(s) to use, can be None
    :type filter_: list or Filter
    :param writer: the writer to use
    :type writer: Writer
    :param session: the session object to use
    :type session: Session
    """
    data = []
    while not reader.has_finished():
        for item in reader.read():
            if item is None:
                continue
            session.count += 1
            data.append(item)
            if session.count % session.options.update_interval == 0:
                session.logger.info("%d records read..." % session.count)

    if filter_ is not None:
        data = filter_.process(data)
        session.logger.info("%d records filtered..." % session.count)
        if not isinstance(data, list):
            data = [data]

    if writer is not None:
        if isinstance(writer, StreamWriter):
            count = 0
            for item in data:
                count += 1
                writer.write_stream(item)
                if count % session.options.update_interval == 0:
                    session.logger.info("%d records written..." % count)
        elif isinstance(writer, BatchWriter):
            writer.write_batch(data)
        else:
            raise Exception("Neither stream nor batch writer: %s" % str(type(writer)))


def execute(reader: Reader, filters: Optional[Union[Filter, List[Filter]]], writer: Writer,
            session: Session = None):
    """
    Executes the pipeline.

    :param reader: the reader to use
    :type reader: Reader
    :param filters: the filter(s) to use, can be None
    :type filters: list or Filter
    :param writer: the writer to use
    :type writer: Writer
    :param session: the session object to use, creates default one if None
    :type session: Session
    """
    # assemble filter
    if isinstance(filters, Filter):
        filter_ = filters
    elif isinstance(filters, list):
        filter_ = MultiFilter(filters=filters)
    elif filters is None:
        filter_ = None
    else:
        raise Exception("Unhandled filter(s) type: %s" % str(type(filters)))

    # propagate session
    if session is None:
        session = Session()
    reader.session = session
    if filter_ is not None:
        filter_.session = session
    if writer is not None:
        writer.session = session

    # initialize
    if isinstance(reader, Initializable) and not init_initializable(reader, "reader"):
        return
    if (filter_ is not None) and isinstance(filter_, Initializable) and not init_initializable(filter_, "filter"):
        return
    if (writer is not None) and isinstance(writer, Initializable) and not init_initializable(writer, "writer"):
        return

    # process data
    try:
        if session.options.force_batch or isinstance(writer, BatchWriter):
            _batch_execution(reader, filter_, writer, session)
        else:
            _stream_execution(reader, filter_, writer, session)
        session.logger.info("%d records processed in total." % session.count)
    except:
        traceback.print_exc()

    # clean up
    if isinstance(reader, Initializable):
        reader.finalize()
    if (filter_ is not None) and isinstance(filter_, Initializable):
        filter_.finalize()
    if (writer is not None) and isinstance(writer, Initializable):
        writer.finalize()
