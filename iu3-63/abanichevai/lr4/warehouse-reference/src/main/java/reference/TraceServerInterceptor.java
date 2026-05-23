package reference;

import io.grpc.ForwardingServerCall;
import io.grpc.Metadata;
import io.grpc.ServerCall;
import io.grpc.ServerCallHandler;
import io.grpc.ServerInterceptor;
import io.grpc.Status;

import java.util.UUID;
import java.util.logging.Logger;

public class TraceServerInterceptor implements ServerInterceptor {

    public static final Metadata.Key<String> TRACE_ID_KEY =
            Metadata.Key.of("trace-id", Metadata.ASCII_STRING_MARSHALLER);

    private static final Logger LOGGER = Logger.getLogger(TraceServerInterceptor.class.getName());

    @Override
    public <ReqT, RespT> ServerCall.Listener<ReqT> interceptCall(
            ServerCall<ReqT, RespT> call,
            Metadata headers,
            ServerCallHandler<ReqT, RespT> next) {

        String traceId = headers.get(TRACE_ID_KEY);
        if (traceId == null || traceId.isBlank()) {
            traceId = UUID.randomUUID().toString();
        }

        String method = call.getMethodDescriptor().getFullMethodName();
        String finalTraceId = traceId;
        LOGGER.info(() -> "[trace-id=" + finalTraceId + "] gRPC >>> " + method);

        ServerCall<ReqT, RespT> wrappedCall = new ForwardingServerCall.SimpleForwardingServerCall<>(call) {
            @Override
            public void close(Status status, Metadata trailers) {
                logResponseStatus(finalTraceId, method, status);
                super.close(status, trailers);
            }
        };

        return next.startCall(wrappedCall, headers);
    }

    private static void logResponseStatus(String traceId, String method, Status status) {
        String message = "[trace-id=" + traceId + "] gRPC <<< " + method
                + " status=" + status.getCode();
        if (status.getDescription() != null && !status.getDescription().isBlank()) {
            message += " description=" + status.getDescription();
        }
        if (status.isOk()) {
            LOGGER.info(message);
        } else {
            LOGGER.warning(message);
        }
    }
}
