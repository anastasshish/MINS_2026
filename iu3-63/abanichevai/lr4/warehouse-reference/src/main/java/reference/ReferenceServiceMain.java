package reference;

import util.LoggingConfig;
import io.grpc.Server;
import io.grpc.ServerBuilder;

import java.io.IOException;
import java.util.concurrent.TimeUnit;
import java.util.logging.Logger;

public class ReferenceServiceMain {

    private static final Logger LOGGER = Logger.getLogger(ReferenceServiceMain.class.getName());
    private static final int PORT = 50051;

    public static void main(String[] args) throws IOException, InterruptedException {
        LoggingConfig.configure();
        Server server = ServerBuilder.forPort(PORT)
                .intercept(new TraceServerInterceptor())
                .addService(new ReferenceServiceImpl())
                .build()
                .start();

        LOGGER.info("warehouse-reference (Reference Service) запущен на порту " + PORT);

        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            LOGGER.info("Остановка warehouse-reference...");
            try {
                server.shutdown().awaitTermination(5, TimeUnit.SECONDS);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }));

        server.awaitTermination();
    }
}
