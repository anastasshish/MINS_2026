package ru.bmstu.promo;

import ru.bmstu.model.OrderPart;
import ru.bmstu.model.RepairOrder;
import ru.bmstu.util.Validator;

import java.time.Clock;
import java.time.DayOfWeek;
import java.time.LocalDate;

public final class WednesdaySparePartsPromo {

    private static final DayOfWeek PROMO_DAY = DayOfWeek.WEDNESDAY;
    private static final double MIN_PART_PRICE_FOR_DISCOUNT = 300.0;
    private static final double DISCOUNT_RATE = 0.15;

    private final Clock clock;

    public WednesdaySparePartsPromo() {
        this(Clock.systemDefaultZone());
    }

    // можно в тестах передать свою дату
    public WednesdaySparePartsPromo(Clock clock) {
        Validator.requireNotNull(clock, "clock");
        this.clock = clock;
    }

    public String buildPromoHintForOrder(RepairOrder order) {
        Validator.requireNotNull(order, "order");
        return calculate(order, LocalDate.now(clock)).toHint();
    }

    public PromoResult calculate(RepairOrder order, LocalDate date) {
        Validator.requireNotNull(order, "order");
        Validator.requireNotNull(date, "date");

        if (!isPromoDay(date)) {
            return new PromoResult(
                    false,
                    0.0,
                    0.0,
                    "Акция не действует на выбранную дату. Условие акции: только среда."
            );
        }

        double baselineCost = 0.0;
        double finalCost = 0.0;

        for (OrderPart orderPart : order.getUsedParts()) {
            double lineCost = orderPart.calculateCost();

            baselineCost += lineCost;
            finalCost += calculateDiscountedLineCost(orderPart, lineCost);
        }

        return new PromoResult(
                true,
                baselineCost,
                finalCost,
                "Акция применена: скидка 15% на запчасти с ценой от 300 включительно за штуку по средам."
        );
    }

    private static boolean isPromoDay(LocalDate date) {
        return date.getDayOfWeek() == PROMO_DAY;
    }

    private static double calculateDiscountedLineCost(OrderPart orderPart, double lineCost) {
        if (qualifiesForDiscount(orderPart)) {
            return lineCost * (1.0 - DISCOUNT_RATE);
        }
        return lineCost;
    }

    private static boolean qualifiesForDiscount(OrderPart orderPart) {
        return orderPart.getPart().getPrice() >= MIN_PART_PRICE_FOR_DISCOUNT;
    }
}