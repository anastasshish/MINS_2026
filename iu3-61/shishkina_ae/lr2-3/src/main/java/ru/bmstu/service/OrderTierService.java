package ru.bmstu.service;

import ru.bmstu.exceptions.OrderNotFoundException;
import ru.bmstu.util.Validator;

import java.util.HashSet;
import java.util.Set;

public class OrderTierService {
    private final Set<Long> vipOrderIds = new HashSet<>();
    private final Set<Long> knownOrderIds = new HashSet<>();

    public void registerOrder(Long orderId) {
        Validator.requireNotNull(orderId, "orderId");
        knownOrderIds.add(orderId);
    }

    public void setVip(Long orderId, boolean isVip) {
        Validator.requireNotNull(orderId, "orderId");
        ensureOrderExists(orderId);
        if (isVip) {
            vipOrderIds.add(orderId);
        } else {
            vipOrderIds.remove(orderId);
        }
    }

    public PricingMode resolvePricingMode(Long orderId) {
        Validator.requireNotNull(orderId, "orderId");
        ensureOrderExists(orderId);
        return vipOrderIds.contains(orderId) ? PricingMode.VIP : PricingMode.STANDARD;
    }

    private void ensureOrderExists(Long orderId) {
        if (!knownOrderIds.contains(orderId)) {
            throw new OrderNotFoundException(orderId);
        }
    }
}
