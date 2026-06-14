package ru.bmstu.service;

import ru.bmstu.model.OrderPart;
import ru.bmstu.model.RepairOrder;
import ru.bmstu.model.RepairWork;
import ru.bmstu.util.Validator;

public class DefaultOrderPricingService implements OrderPricingService {

    @Override
    public double calculateTotalPrice(RepairOrder order) {
        Validator.requireNotNull(order, "order");

        double total = 0.0;
        for (RepairWork work : order.getWorks()) {
            total += work.getPrice();
        }
        for (OrderPart orderPart : order.getUsedParts()) {
            total += orderPart.calculateCost();
        }

        //O if (total > 10000) total *= 0.9;
        
        return total;
    }

    @Override
    public double calculateTotalStandardHours(RepairOrder order) {
        Validator.requireNotNull(order, "order");

        double total = 0.0;
        for (RepairWork work : order.getWorks()) {
            total += work.getStandardHours();
        }
        return total;
    }
}
