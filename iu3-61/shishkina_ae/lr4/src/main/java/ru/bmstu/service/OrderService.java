package ru.bmstu.service;

import ru.bmstu.model.*;
import ru.bmstu.repository.OrderRepository;
import ru.bmstu.exceptions.OrderNotFoundException;
import ru.bmstu.util.Validator;

import java.util.List;
import java.util.ArrayList;

public class OrderService {
    private final OrderRepository orderRepository;
    private final ReferenceCatalogGateway referenceCatalogGateway;
    private final List<OrderStatusObserver> statusObservers = new ArrayList<>();

    private long nextOrderId = 1;
    private long nextCustomerId = 1;

    public OrderService(OrderRepository orderRepository, ReferenceCatalogGateway referenceCatalogGateway) {
        Validator.requireNotNull(orderRepository, "orderRepository");
        Validator.requireNotNull(referenceCatalogGateway, "referenceCatalogGateway");

        this.orderRepository = orderRepository;
        this.referenceCatalogGateway = referenceCatalogGateway;
    }

    public RepairOrder createOrder(String customerName, String customerPhone, String deviceType, String deviceBrand, String deviceModel, String problemDescription) {
        Customer customer = new Customer(nextCustomerId++, customerName, customerPhone);
        Device device = new Device(deviceType, deviceBrand, deviceModel);
        RepairOrder order = new RepairOrder(nextOrderId++, customer, device, problemDescription);

        orderRepository.save(order);
        return order;
    }

    public RepairOrder getOrderById(Long id) {
        return orderRepository.findById(id)
                .orElseThrow(() -> new OrderNotFoundException(id));
    }

    public List<RepairOrder> getAllOrders() {
        return orderRepository.findAll();
    }

    public void changeOrderStatus(Long orderId, OrderStatus newStatus) {
        Validator.requireNotNull(newStatus, "newStatus");
        RepairOrder order = getOrderById(orderId);
        OrderStatus oldStatus = order.getStatus();
        order.changeStatus(newStatus);

        if (oldStatus != newStatus) {
            notifyStatusChanged(order, oldStatus, newStatus);
        }
    }

    public void addWorkToOrder(Long orderId, RepairWork work) {
        Validator.requireNotNull(work, "work");
        RepairOrder order = getOrderById(orderId);
        order.addWork(work);
    }

    public void addPartToOrder(Long orderId, Long partId, int quantity) {
        Validator.requirePositive(quantity, "quantity");

        RepairOrder order = getOrderById(orderId);
        Part part = referenceCatalogGateway.getPartById(partId);

        referenceCatalogGateway.consumePart(partId, quantity);
        order.addPart(part, quantity);
    }

    public void addStatusObserver(OrderStatusObserver observer) {
        Validator.requireNotNull(observer, "observer");
        statusObservers.add(observer);
    }

    private void notifyStatusChanged(RepairOrder order, OrderStatus oldStatus, OrderStatus newStatus) {
        for (OrderStatusObserver observer : statusObservers) {
            observer.onStatusChanged(order, oldStatus, newStatus);
        }
    }
}