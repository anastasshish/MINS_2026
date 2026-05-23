package reference;

import io.grpc.stub.StreamObserver;
import warehouse.reference.grpc.CanStoreTogetherRequest;
import warehouse.reference.grpc.CanStoreTogetherResponse;
import warehouse.reference.grpc.CategoryInfo;
import warehouse.reference.grpc.ListCategoriesRequest;
import warehouse.reference.grpc.ListCategoriesResponse;
import warehouse.reference.grpc.NeighborhoodRadiusRequest;
import warehouse.reference.grpc.NeighborhoodRadiusResponse;
import warehouse.reference.grpc.ProductCategory;
import warehouse.reference.grpc.ReferenceServiceGrpc;
import warehouse.reference.grpc.ValidateProductRequest;
import warehouse.reference.grpc.ValidateProductResponse;

import java.util.EnumMap;
import java.util.Map;
import java.util.Set;
import java.util.logging.Logger;

public class ReferenceServiceImpl extends ReferenceServiceGrpc.ReferenceServiceImplBase {

    private static final Logger LOGGER = Logger.getLogger(ReferenceServiceImpl.class.getName());
    private static final int NEIGHBORHOOD_RADIUS = 5;

    private static final Set<Set<ProductCategory>> INCOMPATIBLE_PAIRS = Set.of(
            Set.of(ProductCategory.FOOD, ProductCategory.CHEMICALS)
    );

    private static final Map<ProductCategory, String> CATEGORY_NAMES = new EnumMap<>(ProductCategory.class);

    static {
        CATEGORY_NAMES.put(ProductCategory.FOOD, "Продукты питания");
        CATEGORY_NAMES.put(ProductCategory.CHEMICALS, "Химия");
        CATEGORY_NAMES.put(ProductCategory.ELECTRONICS, "Электроника");
    }

    @Override
    public void validateProduct(ValidateProductRequest request, StreamObserver<ValidateProductResponse> responseObserver) {
        LOGGER.info("ValidateProduct id=" + request.getProductId());

        String error = validateProductFields(request);
        ValidateProductResponse response = ValidateProductResponse.newBuilder()
                .setValid(error == null)
                .setErrorMessage(error == null ? "" : error)
                .build();

        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }

    @Override
    public void canStoreTogether(CanStoreTogetherRequest request, StreamObserver<CanStoreTogetherResponse> responseObserver) {
        LOGGER.info("CanStoreTogether " + request.getCategoryA() + " + " + request.getCategoryB());

        boolean allowed = canStoreTogetherInternal(request.getCategoryA(), request.getCategoryB());
        CanStoreTogetherResponse.Builder builder = CanStoreTogetherResponse.newBuilder().setAllowed(allowed);
        if (!allowed) {
            builder.setReason("Товарное соседство нарушено: " + displayName(request.getCategoryA())
                    + " нельзя хранить рядом с " + displayName(request.getCategoryB()));
        }

        responseObserver.onNext(builder.build());
        responseObserver.onCompleted();
    }

    @Override
    public void listCategories(ListCategoriesRequest request, StreamObserver<ListCategoriesResponse> responseObserver) {
        LOGGER.info("ListCategories");

        ListCategoriesResponse.Builder responseBuilder = ListCategoriesResponse.newBuilder();
        for (Map.Entry<ProductCategory, String> entry : CATEGORY_NAMES.entrySet()) {
            responseBuilder.addCategories(CategoryInfo.newBuilder()
                    .setCategory(entry.getKey())
                    .setDisplayName(entry.getValue())
                    .build());
        }

        responseObserver.onNext(responseBuilder.build());
        responseObserver.onCompleted();
    }

    @Override
    public void getNeighborhoodRadius(NeighborhoodRadiusRequest request, StreamObserver<NeighborhoodRadiusResponse> responseObserver) {
        LOGGER.info("GetNeighborhoodRadius");

        responseObserver.onNext(NeighborhoodRadiusResponse.newBuilder()
                .setRadius(NEIGHBORHOOD_RADIUS)
                .build());
        responseObserver.onCompleted();
    }

    private static String validateProductFields(ValidateProductRequest request) {
        if (request.getProductId() == null || request.getProductId().trim().isEmpty()) {
            return "ID товара обязателен";
        }
        if (request.getName() == null || request.getName().trim().isEmpty()) {
            return "Название товара обязательно";
        }
        if (request.getCellPosition() < 0) {
            return "Некорректный номер ячейки";
        }
        if (request.getQuantity() < 0) {
            return "Количество должно быть неотрицательным";
        }
        if (request.getCategory() == ProductCategory.PRODUCT_CATEGORY_UNSPECIFIED) {
            return "Категория товара обязательна";
        }
        return null;
    }

    private static boolean canStoreTogetherInternal(ProductCategory a, ProductCategory b) {
        if (a == b) {
            return true;
        }
        if (a == ProductCategory.PRODUCT_CATEGORY_UNSPECIFIED || b == ProductCategory.PRODUCT_CATEGORY_UNSPECIFIED) {
            return false;
        }
        return !INCOMPATIBLE_PAIRS.contains(Set.of(a, b));
    }

    private static String displayName(ProductCategory category) {
        return CATEGORY_NAMES.getOrDefault(category, category.name());
    }
}
