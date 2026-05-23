package grpc;

import exception.ReferenceServiceUnavailableException;
import exception.ValidationException;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.Status;
import io.grpc.StatusRuntimeException;
import model.Product;
import model.ProductCategory;
import warehouse.reference.grpc.CanStoreTogetherRequest;
import warehouse.reference.grpc.CanStoreTogetherResponse;
import warehouse.reference.grpc.CategoryInfo;
import warehouse.reference.grpc.ListCategoriesRequest;
import warehouse.reference.grpc.ListCategoriesResponse;
import warehouse.reference.grpc.NeighborhoodRadiusRequest;
import warehouse.reference.grpc.NeighborhoodRadiusResponse;
import warehouse.reference.grpc.ReferenceServiceGrpc;
import warehouse.reference.grpc.ValidateProductRequest;
import warehouse.reference.grpc.ValidateProductResponse;

import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import java.util.logging.Logger;

public class ReferenceClient implements AutoCloseable {

    private static final Logger LOGGER = Logger.getLogger(ReferenceClient.class.getName());
    private static final String UNAVAILABLE_MESSAGE =
            "Справочный сервис недоступен. Операция не выполнена.";

    private final ManagedChannel channel;
    private final ReferenceServiceGrpc.ReferenceServiceBlockingStub stub;

    public ReferenceClient(String host, int port) {
        channel = ManagedChannelBuilder.forAddress(host, port)
                .usePlaintext()
                .build();
        stub = ReferenceServiceGrpc.newBlockingStub(channel)
                .withInterceptors(new TraceClientInterceptor());
    }

    public void validateAddProduct(Product product, int cellPosition) throws ValidationException, ReferenceServiceUnavailableException {
        ValidateProductResponse response = callReference(() -> stub.validateProduct(ValidateProductRequest.newBuilder()
                .setProductId(product.getId())
                .setName(product.getName())
                .setQuantity(product.getQuantity())
                .setCellPosition(cellPosition)
                .setCategory(toGrpcCategory(product.getCategory()))
                .build()));

        if (!response.getValid()) {
            throw new ValidationException(response.getErrorMessage());
        }
    }

    public void ensureCanStoreTogether(ProductCategory a, ProductCategory b)
            throws ValidationException, ReferenceServiceUnavailableException {
        CanStoreTogetherResponse response = callReference(() -> stub.canStoreTogether(CanStoreTogetherRequest.newBuilder()
                .setCategoryA(toGrpcCategory(a))
                .setCategoryB(toGrpcCategory(b))
                .build()));

        if (!response.getAllowed()) {
            throw new ValidationException(response.getReason());
        }
    }

    public List<CategoryInfo> listCategories() throws ReferenceServiceUnavailableException {
        ListCategoriesResponse response = callReference(
                () -> stub.listCategories(ListCategoriesRequest.getDefaultInstance()));
        return response.getCategoriesList();
    }

    public int getNeighborhoodRadius() throws ReferenceServiceUnavailableException {
        NeighborhoodRadiusResponse response = callReference(
                () -> stub.getNeighborhoodRadius(NeighborhoodRadiusRequest.getDefaultInstance()));
        return response.getRadius();
    }

    /**
     * При падении Reference Service gRPC-канал может остаться в плохом состоянии.
     * После перезапуска Reference делаем одну повторную попытку с resetConnectBackoff().
     */
    private <T> T callReference(Supplier<T> call) throws ReferenceServiceUnavailableException {
        try {
            return call.get();
        } catch (StatusRuntimeException first) {
            if (first.getStatus().getCode() != Status.Code.UNAVAILABLE) {
                throw toUnavailable(first);
            }
            LOGGER.info(() -> "[trace-id=" + TraceContext.get() + "] Повторное подключение к Reference Service...");
            channel.resetConnectBackoff();
            try {
                return call.get();
            } catch (StatusRuntimeException second) {
                throw toUnavailable(second);
            }
        }
    }

    private ReferenceServiceUnavailableException toUnavailable(StatusRuntimeException e) {
        return new ReferenceServiceUnavailableException(UNAVAILABLE_MESSAGE);
    }

    public ProductCategory fromGrpcCategory(warehouse.reference.grpc.ProductCategory category) {
        return switch (category) {
            case FOOD -> ProductCategory.FOOD;
            case CHEMICALS -> ProductCategory.CHEMICALS;
            case ELECTRONICS -> ProductCategory.ELECTRONICS;
            default -> throw new IllegalArgumentException("Неизвестная категория: " + category);
        };
    }

    private static warehouse.reference.grpc.ProductCategory toGrpcCategory(ProductCategory category) {
        return switch (category) {
            case FOOD -> warehouse.reference.grpc.ProductCategory.FOOD;
            case CHEMICALS -> warehouse.reference.grpc.ProductCategory.CHEMICALS;
            case ELECTRONICS -> warehouse.reference.grpc.ProductCategory.ELECTRONICS;
        };
    }

    @Override
    public void close() {
        channel.shutdown();
        try {
            channel.awaitTermination(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
