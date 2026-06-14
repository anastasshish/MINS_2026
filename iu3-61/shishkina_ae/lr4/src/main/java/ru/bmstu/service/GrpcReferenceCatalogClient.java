package ru.bmstu.service;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.Status;
import io.grpc.StatusRuntimeException;
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

import java.util.List;


public class GrpcReferenceCatalogClient implements ReferenceCatalogGateway, AutoCloseable {
    private static final String SERVICE_NAME = "core-service";

    private final ManagedChannel channel;
    private final ReferenceServiceGrpc.ReferenceServiceBlockingStub stub;

    public GrpcReferenceCatalogClient(String host, int port) {
        this.channel = ManagedChannelBuilder.forAddress(host, port).usePlaintext().build();
        this.stub = ReferenceServiceGrpc.newBlockingStub(channel);
    }

    @Override
    public Part getPartById(Long id) {
        try {
            PartDto dto = stub.getPartById(GetPartByIdRequest.newBuilder()
                    .setTraceId(TraceContext.getOrCreate())
                    .setPartId(id)
                    .build());
            ServiceLog.info(SERVICE_NAME, "Получена запчасть #" + id + " из reference-service");
            return toPart(dto);
        } catch (StatusRuntimeException e) {
            throw mapGrpcError("Не удалось получить запчасть", e);
        }
    }

    @Override
    public List<Part> getAllParts() {
        try {
            PartListResponse response = stub.listParts(TraceEnvelope.newBuilder()
                    .setTraceId(TraceContext.getOrCreate())
                    .build());
            ServiceLog.info(SERVICE_NAME, "Получен список запчастей из reference-service");
            return response.getPartsList().stream().map(this::toPart).toList(); //!!!!!
        } catch (StatusRuntimeException e) {
            throw mapGrpcError("Не удалось получить список запчастей", e);
        }
    }

    @Override
    public Part createPart(String name, double price, int quantityInStock) {
        try {
            PartDto dto = stub.createPart(CreatePartRequest.newBuilder()
                    .setTraceId(TraceContext.getOrCreate())
                    .setName(name)
                    .setPrice(price)
                    .setQuantityInStock(quantityInStock)
                    .build());
            ServiceLog.info(SERVICE_NAME, "Создана запчасть через reference-service: " + name);
            return toPart(dto);
        } catch (StatusRuntimeException e) {
            throw mapGrpcError("Не удалось создать запчасть", e);
        }
    }

    @Override
    public void consumePart(Long partId, int amount) {
        try {
            stub.consumePart(ConsumePartRequest.newBuilder()
                    .setTraceId(TraceContext.getOrCreate())
                    .setPartId(partId)
                    .setAmount(amount)
                    .build());
            ServiceLog.info(SERVICE_NAME, "Списание запчасти #" + partId + " подтверждено reference-service");
        } catch (StatusRuntimeException e) {
            throw mapGrpcError("Не удалось списать запчасть", e);
        }
    }

    private Part toPart(PartDto dto) {
        return new Part(dto.getId(), dto.getArticle(), dto.getName(), dto.getPrice(), dto.getQuantityInStock());
    }

    private WorkshopException mapGrpcError(String operation, StatusRuntimeException e) {
        if (e.getStatus().getCode() == Status.Code.UNAVAILABLE) {
            return new WorkshopException("Сервис справочников недоступен");
        }
        String details = e.getStatus().getDescription() == null ? e.getMessage() : e.getStatus().getDescription();
        return new WorkshopException(operation + ": " + details);
    }

    @Override
    public void close() {
        channel.shutdownNow();
    }
}
