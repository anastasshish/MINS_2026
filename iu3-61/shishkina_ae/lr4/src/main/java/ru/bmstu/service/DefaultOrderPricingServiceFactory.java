package ru.bmstu.service;

import ru.bmstu.util.Validator;

public class DefaultOrderPricingServiceFactory implements OrderPricingServiceFactory {
    @Override
    public OrderPricingService create(PricingMode mode) {
        Validator.requireNotNull(mode, "mode");

        return switch (mode) {
            case STANDARD -> new DefaultOrderPricingService();
            case VIP -> new VipOrderPricingService();
        };
    }
}
