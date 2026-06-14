package ru.bmstu.grpc;

import io.grpc.Status;
import io.grpc.stub.StreamObserver;
import ru.bmstu.exceptions.ValidationException;
import ru.bmstu.exceptions.WorkshopException;
import ru.bmstu.grpc.reference.ConsumePartRequest;
import ru.bmstu.grpc.reference.CreatePartRequest;
import ru.bmstu.grpc.reference.GetPartByIdRequest;
import ru.bmstu.grpc.reference.PartDto;
import ru.bmstu.grpc.reference.PartListResponse;
import ru.bmstu.grpc.reference.ReferenceServiceGrpc;
import ru.bmstu.grpc.reference.TraceEnvelope;
import ru.bmstu.infra.ServiceLog;
import ru.bmstu.infra.TraceContext;
import ru.bmstu.model.Part;
import ru.bmstu.service.InventoryService;

//реализует gRPC сервис прописанный в proto
public class ReferenceGrpcService extends ReferenceServiceGrpc.ReferenceServiceImplBase {
    private static final String SERVICE_NAME = "reference-service";
    private final InventoryService inventoryService;

    public ReferenceGrpcService(InventoryService inventoryService) {
        this.inventoryService = inventoryService;
    }

    @Override
    public void getPartById(GetPartByIdRequest request, StreamObserver<PartDto> responseObserver) {
        withTrace(request.getTraceId(), () -> {
            ServiceLog.info(SERVICE_NAME, "GetPartById partId=" + request.getPartId());
            Part part = inventoryService.getPartById(request.getPartId());
            responseObserver.onNext(toDto(part));
            responseObserver.onCompleted();
        }, responseObserver);
    }

    @Override
    public void listParts(TraceEnvelope request, StreamObserver<PartListResponse> responseObserver) {
        withTrace(request.getTraceId(), () -> {
            ServiceLog.info(SERVICE_NAME, "ListParts");
            PartListResponse.Builder response = PartListResponse.newBuilder();
            for (Part part : inventoryService.getAllParts()) {
                response.addParts(toDto(part));
            }
            responseObserver.onNext(response.build());
            responseObserver.onCompleted();
        }, responseObserver);
    }

    @Override
    public void createPart(CreatePartRequest request, StreamObserver<PartDto> responseObserver) {
        withTrace(request.getTraceId(), () -> {
            ServiceLog.info(SERVICE_NAME, "CreatePart name=" + request.getName());
            Part part = inventoryService.createPart(request.getName(), request.getPrice(), request.getQuantityInStock());
            responseObserver.onNext(toDto(part));
            responseObserver.onCompleted();
        }, responseObserver);
    }

    @Override
    public void consumePart(ConsumePartRequest request, StreamObserver<TraceEnvelope> responseObserver) {
        withTrace(request.getTraceId(), () -> {
            ServiceLog.info(SERVICE_NAME, "ConsumePart partId=" + request.getPartId() + ", amount=" + request.getAmount());
            inventoryService.consumePart(request.getPartId(), request.getAmount());
            responseObserver.onNext(TraceEnvelope.newBuilder().setTraceId(TraceContext.getOrCreate()).build());
            responseObserver.onCompleted();
        }, responseObserver);
    }

    private PartDto toDto(Part part) {
        return PartDto.newBuilder()
                .setId(part.getId())
                .setArticle(part.getArticle())
                .setName(part.getName())
                .setPrice(part.getPrice())
                .setQuantityInStock(part.getQuantityInStock())
                .build();
    }

    private <T> void withTrace(String traceId, Runnable action, StreamObserver<T> responseObserver) {
        try {
            TraceContext.set(traceId == null || traceId.isBlank() ? TraceContext.beginTrace() : traceId);
            action.run();

            //неверные аргументы
        }catch (ValidationException e) {
                responseObserver.onError(Status.INVALID_ARGUMENT.withDescription(e.getMessage()).asRuntimeException());
        } catch (WorkshopException e) {
            //запчасть есть, запрос корректный, но на складе недостаточно количества
            responseObserver.onError(Status.FAILED_PRECONDITION.withDescription(e.getMessage()).asRuntimeException());
            //остальное
        } catch (Exception e) {
            responseObserver.onError(Status.INTERNAL.withDescription(e.getMessage()).asRuntimeException());
        } finally {
            TraceContext.clear();
        }
    }
}
