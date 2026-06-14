package ru.bmstu.infra;

import java.util.UUID;

public final class TraceContext {
    private static final ThreadLocal<String> TRACE_ID = new ThreadLocal<>();

    public static String beginTrace() {
        String traceId = UUID.randomUUID().toString();
        TRACE_ID.set(traceId);
        return traceId;
    }

    public static void set(String traceId) {
        TRACE_ID.set(traceId);
    }

    public static String getOrCreate() {
        String traceId = TRACE_ID.get();
        if (traceId == null || traceId.isBlank()) {
            return beginTrace();
        }
        return traceId;
    }

    public static void clear() {
        TRACE_ID.remove();
    }
}
