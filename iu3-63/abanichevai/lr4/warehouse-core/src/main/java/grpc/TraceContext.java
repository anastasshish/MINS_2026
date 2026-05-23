package grpc;

import java.util.UUID;

public final class TraceContext {

    private static final ThreadLocal<String> CURRENT = new ThreadLocal<>();

    private TraceContext() {
    }

    public static void set(String traceId) {
        CURRENT.set(traceId);
    }

    public static String get() {
        String traceId = CURRENT.get();
        return traceId != null ? traceId : UUID.randomUUID().toString();
    }

    public static void clear() {
        CURRENT.remove();
    }
}
