package ru.bmstu.service;

public interface OrderPricingServiceFactory {
    OrderPricingService create(PricingMode mode);
}
