package ru.bmstu.model;

import ru.bmstu.util.Validator;

import java.util.ArrayList;
import java.util.List;

public class RepairOrder {
    private final Long id;
    private final Customer customer;
    private final Device device;
    private final String problemDescription;
    private OrderStatus status;
    private final List<RepairWork> works;
    private final List<OrderPart> usedParts;

    public RepairOrder(Long id, Customer customer, Device device, String problemDescription) {
        Validator.requireNotNull(id, "id");
        Validator.requireNotNull(customer, "customer");
        Validator.requireNotNull(device, "device");
        Validator.requireNonBlank(problemDescription, "problemDescription");

        this.id = id;
        this.customer = customer;
        this.device = device;
        this.problemDescription = problemDescription;
        this.status = OrderStatus.CREATED;
        this.works = new ArrayList<>();
        this.usedParts = new ArrayList<>();
    }

    public Long getId() {
        return id;
    }

    public Customer getCustomer() {
        return customer;
    }

    public Device getDevice() {
        return device;
    }

    public String getProblemDescription() {
        return problemDescription;
    }

    public OrderStatus getStatus() {
        return status;
    }

    public List<RepairWork> getWorks() {
        return new ArrayList<>(works);
    }

    public List<OrderPart> getUsedParts() {
        return new ArrayList<>(usedParts);
    }

    public void changeStatus(OrderStatus newStatus) {
        Validator.requireNotNull(newStatus, "newStatus");


        this.status = newStatus;
    }

    public void addWork(RepairWork work) {
        Validator.requireNotNull(work, "work");
        works.add(work);
    }

    public void addPart(Part part, int quantity) {
        Validator.requireNotNull(part, "part");
        Validator.requirePositive(quantity, "quantity");

        OrderPart existingOrderPart = findOrderPartByArticle(part.getArticle());

        if (existingOrderPart != null) {
            existingOrderPart.increaseQuantity(quantity);
        } else {
            usedParts.add(new OrderPart(part, quantity));
        }
    }

    public double calculateTotalPrice() {
        double total = 0.0;

        for (RepairWork work : works) {
            total += work.getPrice();
        }

        for (OrderPart orderPart : usedParts) {
            total += orderPart.calculateCost();
        }

        return total;
    }

    public double calculateTotalStandardHours() {
        double total = 0.0;

        for (RepairWork work : works) {
            total += work.getStandardHours();
        }

        return total;
    }

    private OrderPart findOrderPartByArticle(String article) {
        for (OrderPart orderPart : usedParts) {
            if (orderPart.getPart().getArticle().equals(article)) {
                return orderPart;
            }
        }
        return null;
    }

    private boolean isValidStatusTransition(OrderStatus currentStatus, OrderStatus newStatus) {
        if (currentStatus == newStatus) {
            return true;
        }

        return switch (currentStatus) {
            case CREATED -> newStatus == OrderStatus.PROGRESS || newStatus == OrderStatus.WAITING_PARTS || newStatus == OrderStatus.CANCELLED;

            case PROGRESS -> newStatus == OrderStatus.WAITING_PARTS || newStatus == OrderStatus.COMPLETED || newStatus == OrderStatus.CANCELLED;

            case WAITING_PARTS -> newStatus == OrderStatus.PROGRESS || newStatus == OrderStatus.CANCELLED;

            case COMPLETED, CANCELLED -> false;
        };
    }

    @Override
    public String toString() {
        return "RepairOrder{id=" + id + ", customer=" + customer + ", device=" + device + ", problemDescription='" + problemDescription + '\'' + ", status=" + status + ", works=" + works + ", usedParts=" + usedParts + ", totalPrice=" + calculateTotalPrice() + ", totalStandardHours=" + calculateTotalStandardHours() + '}';
    }


}