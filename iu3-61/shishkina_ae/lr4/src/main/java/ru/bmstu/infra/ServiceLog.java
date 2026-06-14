package ru.bmstu.infra;

public final class ServiceLog {
    private ServiceLog() {
    }

    public static void info(String service, String message) {
        System.out.println("[" + service + "] [traceId=" + TraceContext.getOrCreate() + "] " + message);
    }
}
