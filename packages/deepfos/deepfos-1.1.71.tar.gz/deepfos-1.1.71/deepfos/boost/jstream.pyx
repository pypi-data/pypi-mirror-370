from libc.string cimport strlen


cpdef read(char *stream, object streamer):
    cdef int index = 0
    cdef char* empty = ''
    cdef int stream_len = strlen(stream)
    cdef char* cp_stream = stream
    cdef char c
    cdef int i
    cdef int matched_index = streamer.matched_index
    cdef char* key = streamer.key
    cdef bint is_started = streamer.is_started
    cdef bint in_double_quotation = streamer.in_double_quotation
    cdef bint in_escape = streamer.in_escape
    cdef int lbrace = streamer.lbrace
    cdef int rbrace = streamer.rbrace
    cdef bint finished = False
    
    for i in range(stream_len):
        c = cp_stream[i]
        if 0 < matched_index < strlen(key) and c != key[matched_index]:
            matched_index = 0
        if in_double_quotation and not is_started and matched_index < strlen(key) and c == key[matched_index]:
            matched_index += 1

        if c == '\\':
            if not in_escape:
                in_escape = True
            else:
                in_escape = False
            index += 1
            continue

        if not in_escape and c == '"' and not in_double_quotation:
            in_double_quotation = True
        elif not in_escape and c == '"' and in_double_quotation:
            in_double_quotation = False

        if not in_double_quotation and is_started and (c == '{' or c =='['):
            lbrace += 1

        if not in_double_quotation and is_started and (c == '}' or c ==']'):
            rbrace += 1

        # for value with brace
        if is_started and lbrace > 0 and rbrace > 0 and lbrace - rbrace == 0:
            finished = True
            index += 1
            break

        # other
        if is_started and not in_double_quotation and c == ',' and lbrace == 0 and rbrace == 0:
            finished = True
            break

        if is_started and not in_double_quotation and (c == '}' or c == ']') and lbrace == 0 and rbrace == 1:
            finished = True
            break

        index += 1

        if strlen(key) == matched_index and not is_started and c == ':':
            is_started = True
            stream = stream + index * sizeof(char)
            index = 0

        if in_escape:
            in_escape = False

    if is_started:
        streamer.finished = finished
        stream[index*sizeof(char)] = '\0'
        if not finished:
            streamer.matched_index = matched_index
            streamer.key = key
            streamer.is_started = is_started
            streamer.in_double_quotation = in_double_quotation
            streamer.in_escape = in_escape
            streamer.lbrace = lbrace
            streamer.rbrace = rbrace
        return stream
    else:
        streamer.matched_index = matched_index
        streamer.key = key
        streamer.is_started = is_started
        streamer.in_double_quotation = in_double_quotation
        streamer.in_escape = in_escape
        streamer.lbrace = lbrace
        streamer.rbrace = rbrace
        streamer.is_started = is_started
        return empty
