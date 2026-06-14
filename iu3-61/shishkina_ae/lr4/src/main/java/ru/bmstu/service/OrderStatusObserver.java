package ru.bmstu.service;

import ru.bmstu.model.OrderStatus;
import ru.bmstu.model.RepairOrder;

public interface OrderStatusObserver {
    void onStatusChanged(RepairOrder order, OrderStatus oldStatus, OrderStatus newStatus);
}
