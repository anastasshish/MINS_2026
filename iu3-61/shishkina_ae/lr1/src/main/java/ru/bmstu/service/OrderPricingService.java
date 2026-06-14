package ru.bmstu.service;

import ru.bmstu.model.RepairOrder;

public interface OrderPricingService {
    double calculateTotalPrice(RepairOrder order);

    double calculateTotalStandardHours(RepairOrder order);
}
