package grpc;

import io.grpc.CallOptions;
import io.grpc.Channel;
import io.grpc.ClientCall;
import io.grpc.ClientInterceptor;
import io.grpc.ForwardingClientCall;
import io.grpc.ForwardingClientCallListener;
import io.grpc.Metadata;
import io.grpc.MethodDescriptor;
import io.grpc.Status;

import java.util.logging.Logger;

public class TraceClientInterceptor implements ClientInterceptor {

    public static final Metadata.Key<String> TRACE_ID_KEY =
            Metadata.Key.of("trace-id", Metadata.ASCII_STRING_MARSHALLER);

    private static final Logger LOGGER = Logger.getLogger(TraceClientInterceptor.class.getName());

    @Override
    public <ReqT, RespT> ClientCall<ReqT, RespT> interceptCall(
            MethodDescriptor<ReqT, RespT> method,
            CallOptions callOptions,
            Channel next) {

        String traceId = TraceContext.get();
        String methodName = method.getFullMethodName();
        LOGGER.info(() -> "[trace-id=" + traceId + "] gRPC -> " + methodName);

        return new ForwardingClientCall.SimpleForwardingClientCall<>(next.newCall(method, callOptions)) {
            @Override
            public void start(Listener<RespT> responseListener, Metadata headers) {
                headers.put(TRACE_ID_KEY, traceId);
                super.start(new ForwardingClientCallListener.SimpleForwardingClientCallListener<>(responseListener) {
                    @Override
                    public void onClose(Status status, Metadata trailers) {
                        logResponseStatus(traceId, methodName, status);
                        super.onClose(status, trailers);
                    }
                }, headers);
            }
        };
    }

    private static void logResponseStatus(String traceId, String methodName, Status status) {
        String message = "[trace-id=" + traceId + "] gRPC <- " + methodName
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
